from google.cloud import storage
import os

# Constants
BUCKET_NAME = 'innit_articles_bucket'
TRAIN_BLOB_PREFIX = 'train_dataset/'
# Removed VALID_BLOB_PREFIX and TEST_BLOB_PREFIX since they are no longer needed

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


def main(): # pragma: no cover
    # Check if the training dataset exists locally, if not download it from GCP
    download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)
    print("Successfully downloaded the training dataset")

if __name__ == "__main__":
    main() # pragma: no cover
