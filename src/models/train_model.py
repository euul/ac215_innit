import pandas as pd
import json
from datasets import Dataset, load_from_disk
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
import torch
import wandb
import torch.nn.functional as F
import argparse
from google.cloud import storage
import os

# Constants
BUCKET_NAME = 'innit_articles_bucket'
TRAIN_BLOB_PREFIX = 'train_dataset/'
VALID_BLOB_PREFIX = 'valid_dataset/'
TEST_BLOB_PREFIX = 'test_dataset/'
LOCAL_DATASET_DIR = './datasets'

# Functions
def download_dataset_folder(bucket_name, blob_prefix, local_dataset_dir):
    """Download all files in a GCP folder (blob prefix) to the local directory."""
    local_folder_path = os.path.join(local_dataset_dir, blob_prefix.strip('/'))
    
    if not os.path.exists(local_folder_path):
        print(f"{local_folder_path} does not exist. Downloading from GCS...")
        os.makedirs(local_folder_path, exist_ok=True)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        blobs = bucket.list_blobs(prefix=blob_prefix)
        
        for blob in blobs:
            local_path = os.path.join(local_dataset_dir, blob.name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}")
    else:
        print(f"{local_folder_path} already exists. Skipping download.")

def load_datasets(local_dataset_dir):
    """Load datasets from the local disk."""
    train_dataset = load_from_disk(os.path.join(local_dataset_dir, TRAIN_BLOB_PREFIX.strip('/')))
    valid_dataset = load_from_disk(os.path.join(local_dataset_dir, VALID_BLOB_PREFIX.strip('/')))
    test_dataset = load_from_disk(os.path.join(local_dataset_dir, TEST_BLOB_PREFIX.strip('/')))
    print("Successfully loaded datasets from disk")
    return train_dataset, valid_dataset, test_dataset

def preprocess_function(examples, tokenizer):
    return tokenizer(examples['Transcript'], truncation=True, padding='max_length', max_length=800)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean() * 100
    return {"accuracy": accuracy}

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def main():
    # Setup the arguments for the trainer task
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wandb_key", dest="wandb_key", required=True, type=str, help="WandB API Key"
    )
    args = parser.parse_args()

    # Download datasets
    download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)
    download_dataset_folder(BUCKET_NAME, VALID_BLOB_PREFIX, LOCAL_DATASET_DIR)
    download_dataset_folder(BUCKET_NAME, TEST_BLOB_PREFIX, LOCAL_DATASET_DIR)

    # Load datasets
    train_dataset, valid_dataset, test_dataset = load_datasets(LOCAL_DATASET_DIR)
    print("Successfully loaded datasets")

    # Retrieve class labels
    class_label = train_dataset.features['label']
    label2id = {class_label.names[i]: i for i in range(class_label.num_classes)}
    id2label = {i: class_label.names[i] for i in range(class_label.num_classes)}

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small")

    # Tokenize datasets
    tokenized_train_dataset = train_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    tokenized_valid_dataset = valid_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    tokenized_test_dataset = test_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)

    # Load pre-trained model
    model = AutoModelForSequenceClassification.from_pretrained(
        "microsoft/deberta-v3-small",
        num_labels=len(label2id)
    )

    # Calculate class weights
    class_weights = (1 / pd.DataFrame(train_dataset['label']).value_counts(normalize=True).sort_index()).tolist()
    class_weights = torch.tensor(class_weights)
    class_weights = class_weights / class_weights.sum()

    # Define training arguments
    training_args = TrainingArguments(
        report_to='wandb',
        run_name="lr_2e_5",
        load_best_model_at_end=True,
        metric_for_best_model='accuracy',
        logging_steps=50,
        output_dir="./results",
        eval_strategy="steps",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=5,
        weight_decay=0.01,
        save_total_limit=2
    )

    # Custom Trainer
    class CustomTrainer(Trainer):
        def __init__(self, *args, class_weights=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.class_weights = class_weights if class_weights is not None else None

        def compute_loss(self, model, inputs, return_outputs=False):
            labels = inputs.pop("labels").long()
            outputs = model(**inputs)
            logits = outputs.get('logits')
            loss = F.cross_entropy(logits, labels, weight=self.class_weights) if self.class_weights else F.cross_entropy(logits, labels)
            return (loss, outputs) if return_outputs else loss

    # Log in to WandB
    wandb.login(key=args.wandb_key)
    wandb.init(project="innit-baseline-experiments", name="lr_2e_5")

    # Initialize Trainer
    trainer = CustomTrainer(
        model=model,
        args=training_args,
        class_weights=class_weights,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_valid_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # Train model
    print("Training model")
    trainer.train()

    # Evaluate model
    evaluation_results = trainer.evaluate(tokenized_test_dataset)
    print("Test Set Evaluation Results:", evaluation_results)

    # Save model
    print("Saving model")
    torch.save(model.state_dict(), 'distill_bert_c1_weights.pth')

    # Upload model
    upload_blob(BUCKET_NAME, 'distill_bert_c1_weights.pth', 'distill_bert_c1_weights.pth')

    wandb.finish()
    print("Finished training")

if __name__ == "__main__":
    main()
