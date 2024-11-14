import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset, load_from_disk

from google.cloud import storage
import wandb
import argparse

import os
import numpy as np
import pandas as pd

import wandb

# Setup the arguments for the trainer task
# Setup the arguments for the trainer task
parser = argparse.ArgumentParser()
parser.add_argument(
    "--wandb_key", dest="wandb_key", required=True, type=str, help="WandB API Key"
)
parser.add_argument(
    "--run_name", dest="run_name", default='final', type=str, help="WandB run name"
)
parser.add_argument("--lr", dest="lr", default=0.000002, type=float, help="Learning Rate")
args = parser.parse_args()



NUM_LABELS = 5
BUCKET_NAME = 'innit_articles_bucket'
BLOB_NAME = 'distill_bert_c1_weights.pth'
LOCAL_MODEL_PATH = './distill_bert_c1_weights.pth'
LOCAL_DATASET_DIR = './datasets'

TRAIN_BLOB_PREFIX = 'train_dataset_generated/'
VALID_BLOB_PREFIX = 'valid_dataset/'
TEST_BLOB_PREFIX = 'test_dataset/'

UPLOAD_BLOB_NAME = 'distill_bert_a1_weights.pth'


def download_weights(bucket_name, blob_name, local_model_path):
    """Download model weights from Google Cloud Storage if not already present locally."""
    
    if os.path.exists(local_model_path):
        print(f"{local_model_path} already exists locally. Skipping download.")
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Download the blob to a local file
    blob.download_to_filename(local_model_path)
    print(f"Downloaded model weights from GCS: gs://{bucket_name}/{blob_name}")

def load_model(local_model_path, num_labels):
    """Load the model with the specified weights."""
    model = AutoModelForSequenceClassification.from_pretrained(
        "microsoft/deberta-v3-small",
        num_labels=num_labels
    )
    # Freeze the base DeBERTa layers
    for param in model.deberta.parameters():
        param.requires_grad = False
        
    # Load the weights
    model.load_state_dict(torch.load(local_model_path, map_location=torch.device('cpu')))
    model.eval()  # Set the model to evaluation mode
    print("Model loaded successfully.")
    return model


def download_dataset_folder(bucket_name, blob_prefix, local_dataset_dir):
    """Download all files in a GCP folder (blob prefix) to the local directory."""
    local_folder_path = os.path.join(local_dataset_dir, blob_prefix.strip('/'))
    
    if not os.path.exists(local_folder_path):
        print(f"{local_folder_path} does not exist. Downloading from GCS...")
        os.makedirs(local_folder_path, exist_ok=True)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # List all blobs that start with the given prefix
        blobs = bucket.list_blobs(prefix=blob_prefix)
        
        for blob in blobs:
            # Create directories for nested blobs if necessary
            local_path = os.path.join(local_dataset_dir, blob.name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download each file in the directory
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


# Custom accuracy function that returns percentage accuracy
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # Calculate the accuracy as a percentage
    accuracy = (predictions == labels).mean() * 100  # Convert to percentage

    return {"accuracy": accuracy}


class CustomTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.class_weights = torch.tensor(class_weights,
                                              dtype=torch.float32).to(self.args.device)
        else:
            self.class_weights = None

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels").long()
        outputs = model(**inputs)
        logits = outputs.get('logits')

        if self.class_weights is not None:
            loss = F.cross_entropy(logits, labels, weight=self.class_weights)
        else:
            loss = F.cross_entropy(logits, labels)

        return (loss, outputs) if return_outputs else loss
    

# Load model
download_weights(BUCKET_NAME, BLOB_NAME, LOCAL_MODEL_PATH)
model = load_model(LOCAL_MODEL_PATH, NUM_LABELS)

# Load the datasets
download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)
download_dataset_folder(BUCKET_NAME, VALID_BLOB_PREFIX, LOCAL_DATASET_DIR)
download_dataset_folder(BUCKET_NAME, TEST_BLOB_PREFIX, LOCAL_DATASET_DIR)

train_dataset, valid_dataset, test_dataset = load_datasets(LOCAL_DATASET_DIR)

print("successfully loaded datasets")

# Retrieve the ClassLabel object from the 'label' column of train_dataset
class_label = train_dataset.features['label']
label2id = {class_label.names[i]: i for i in range(class_label.num_classes)}
id2label = {i: class_label.names[i] for i in range(class_label.num_classes)}

# Load RoBERTa tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small") # changed model to small for experiments! (Christian)

# Tokenize the transcripts
def preprocess_function(examples):
    return tokenizer(examples['Transcript'], truncation=True, padding='max_length', max_length=800) #changed from 512

# Apply preprocessing to the train, validation, and test datasets
tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True)
tokenized_valid_dataset = valid_dataset.map(preprocess_function, batched=True)
tokenized_test_dataset = test_dataset.map(preprocess_function, batched=True)


# Calculate class weights for the loss function
class_weights=(1/pd.DataFrame(train_dataset['label']).value_counts(normalize=True).sort_index()).tolist()
class_weights=torch.tensor(class_weights)
class_weights=class_weights/class_weights.sum()

# log in to wandb
wandb.login(key=args.wandb_key)
print("logged in to wandb")

wandb.init(
    project="innit-finetune-experiments", # Ensure this matches your W&B project name
    name=args.run_name # change the name of your specific run here
    )

# Define Training Arguments
training_args = TrainingArguments(
    report_to = 'wandb',                 # enable logging to W&B
    run_name = args.run_name,             # set name of current run
    load_best_model_at_end = True,
    metric_for_best_model = 'accuracy',
    logging_steps = 50,
    output_dir="./results",              # Output directory for model checkpoints      w
    eval_strategy="steps",               # Evaluate after every 50 steps               
    learning_rate = args.lr,             # Learning rate
    per_device_train_batch_size=4,       # Batch size for training
    per_device_eval_batch_size=4,        # Batch size for evaluation
    num_train_epochs=5,                  # Number of training epochs
    weight_decay=0.01,                   # Strength of weight decay
    save_total_limit=2                   # Save only the last 2 models
)

trainer = CustomTrainer(
    model=model,
    args=training_args,
    class_weights = class_weights,
    train_dataset=tokenized_train_dataset,   # Tokenized training set
    eval_dataset=tokenized_valid_dataset,    # Tokenized validation set for evaluation
    tokenizer=tokenizer,
    compute_metrics=compute_metrics          # Custom metrics
)

print("training model")
trainer.train()

evaluation_results = trainer.evaluate(tokenized_test_dataset)
print("Test Set Evaluation Results:", evaluation_results)

# Save the model weights
torch.save(model.state_dict(), UPLOAD_BLOB_NAME)

# Upload the model weights to GCS
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(UPLOAD_BLOB_NAME)
blob.upload_from_filename(UPLOAD_BLOB_NAME)

print(f"File {UPLOAD_BLOB_NAME} uploaded to {UPLOAD_BLOB_NAME}.")

