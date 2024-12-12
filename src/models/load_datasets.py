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


def main(): # pragma: no cover
    # Check if the dataset exists locally, if not download it from GCP
    download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)
    download_dataset_folder(BUCKET_NAME, VALID_BLOB_PREFIX, LOCAL_DATASET_DIR)
    download_dataset_folder(BUCKET_NAME, TEST_BLOB_PREFIX, LOCAL_DATASET_DIR)

    # Load the datasets
    train_dataset, valid_dataset, test_dataset = load_datasets(LOCAL_DATASET_DIR)


    print("successfully loaded datasets")

if __name__ == '__main__': # pragma: no cover
    main()
