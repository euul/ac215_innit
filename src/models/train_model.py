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

# Setup the arguments for the trainer task
parser = argparse.ArgumentParser()
parser.add_argument(
    "--wandb_key", dest="wandb_key", required=True, type=str, help="WandB API Key"
)
args = parser.parse_args()


# Load datasets from GCP bucket

# Constants
BUCKET_NAME = 'innit_articles_bucket'
TRAIN_BLOB_PREFIX = 'train_dataset/'
VALID_BLOB_PREFIX = 'valid_dataset/'
TEST_BLOB_PREFIX = 'test_dataset/'

LOCAL_DATASET_DIR = './datasets'

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


# Check if the dataset exists locally, if not download it from GCP
download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)
download_dataset_folder(BUCKET_NAME, VALID_BLOB_PREFIX, LOCAL_DATASET_DIR)
download_dataset_folder(BUCKET_NAME, TEST_BLOB_PREFIX, LOCAL_DATASET_DIR)

# Load the datasets
train_dataset, valid_dataset, test_dataset = load_datasets(LOCAL_DATASET_DIR)



print("successfully loaded datasets")


# Retrieve the ClassLabel object from the 'label' column of train_dataset
class_label = train_dataset.features['label']

# Extract label2id and id2label mappings
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


# Load the pre-trained RoBERTa model with a classification head
model = AutoModelForSequenceClassification.from_pretrained(
    "microsoft/deberta-v3-small",
    num_labels=len(label2id)
)

# Custom accuracy function that returns percentage accuracy
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # Calculate the accuracy as a percentage
    accuracy = (predictions == labels).mean() * 100  # Convert to percentage

    return {"accuracy": accuracy}

# Define Training Arguments

training_args = TrainingArguments(
    report_to = 'wandb',                 # enable logging to W&B
    run_name = "lr_2e_5",                # set name of current run
    load_best_model_at_end = True,
    metric_for_best_model = 'accuracy',
    logging_steps = 50,
    output_dir="./results",              # Output directory for model checkpoints      w
    eval_strategy="steps",               # Evaluate after every 50 steps
    learning_rate=2e-5,                  # Learning rate
    per_device_train_batch_size=4,       # Batch size for training
    per_device_eval_batch_size=4,        # Batch size for evaluation
    num_train_epochs=5,                  # Number of training epochs
    weight_decay=0.01,                   # Strength of weight decay
    save_total_limit=2                   # Save only the last 2 models
)


# Calculate class weights for the loss function
class_weights=(1/pd.DataFrame(train_dataset['label']).value_counts(normalize=True).sort_index()).tolist()
class_weights=torch.tensor(class_weights)
class_weights=class_weights/class_weights.sum()
# print(class_weights)

class CustomTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.class_weights = torch.tensor(class_weights,
            dtype=torch.float32).to(self.args.device)
        else:
            self.class_weights = None

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels").long()

        outputs = model(**inputs)

        logits = outputs.get('logits')

        if self.class_weights is not None:
            loss = F.cross_entropy(logits, labels, weight=self.class_weights)
        else:
            loss = F.cross_entropy(logits, labels)

        return (loss, outputs) if return_outputs else loss
    

# Log in to W&B using the provided API key
wandb.login(key=args.wandb_key)

print("logged in to wandb")


# Initialize a new W&B run with the updated training arguments
wandb.init(
    project="innit-baseline-experiments", # Ensure this matches your W&B project name
    name="lr_2e_5" # change the name of your specific run here
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

print("saving model")
torch.save(model.state_dict(), 'distill_bert_c1_weights.pth')

wandb.finish() 

print("finished training")



# Upload file to GCP
source_file_name = "distill_bert_c1_weights.pth"  # Path to your file
destination_blob_name = "distill_bert_c1_weights.pth"  # Destination file name in GCS

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# Call the upload function
upload_blob(BUCKET_NAME, source_file_name, destination_blob_name)

