import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_from_disk
from google.cloud import storage
import os

# Constants
NUM_LABELS = 5
BUCKET_NAME = 'innit_articles_bucket'
BLOB_NAME = 'distill_bert_c1_weights.pth'
LOCAL_MODEL_PATH = './distill_bert_c1_weights.pth'
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
    # Load the weights
    model.load_state_dict(torch.load(local_model_path, map_location=torch.device('cpu')))
    model.eval()  # Set the model to evaluation mode
    print("Model loaded successfully.")
    return model

def infer(model, test_dataset):
    """Perform inference on the test dataset."""
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small")

    # Tokenize the test dataset
    tokenized_test_dataset = test_dataset.map(
        lambda examples: tokenizer(examples['Transcript'], truncation=True, padding='max_length', max_length=800),
        batched=True
    )

    # Prepare inputs for the model
    input_ids = tokenized_test_dataset['input_ids']
    attention_mask = tokenized_test_dataset['attention_mask']
    
    # Make predictions
    with torch.no_grad():
        outputs = model(input_ids=torch.tensor(input_ids), attention_mask=torch.tensor(attention_mask))
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
    
    return predictions

if __name__ == "__main__":
    # Step 1: Download weights
    download_weights(BUCKET_NAME, BLOB_NAME, LOCAL_MODEL_PATH)

    # Step 2: Load test dataset
    download_dataset_folder(BUCKET_NAME, TEST_BLOB_PREFIX, LOCAL_DATASET_DIR)
    test_dataset = load_from_disk(os.path.join(LOCAL_DATASET_DIR, TEST_BLOB_PREFIX.strip('/')))

    # Step 3: Load model and perform inference
    num_labels = NUM_LABELS
    model = load_model(LOCAL_MODEL_PATH, num_labels)
    predictions = infer(model, test_dataset)

    print("Predictions:", predictions)
