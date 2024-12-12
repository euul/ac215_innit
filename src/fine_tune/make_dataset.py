import pandas as pd
import json
from datasets import Dataset, load_from_disk
from google.cloud import storage
import os
from datasets import Dataset, ClassLabel

BUCKET_NAME = 'innit_articles_bucket'
LOCAL_DATASET_DIR = './datasets'
file_paths = ["output-A1.json", "output-A2.json", "output-B1.json", "output-B2.json", "output-C1.json"]


def count_elements_and_save_locally(bucket_name, file_path, local_dir):
    """Count elements in a GCS JSON file and save a copy locally."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    if not blob.exists():
        print(f"File {file_path} does not exist in bucket {bucket_name}.")
        return None
    
    # Download JSON file content
    data = json.loads(blob.download_as_text())
    
    # Save locally
    local_path = os.path.join(local_dir, file_path)
    with open(local_path, 'w') as local_file:
        json.dump(data, local_file, indent=4)
    
    print(f"File {file_path} saved locally at {local_path}")
    return len(data)


def create_dataframe():
    data_frames = []
    
    labels = ['A1', 'A2', 'B1', 'B2', 'C1']

    for label in labels:
        # Load the JSON data for each label
        with open(f'{LOCAL_DATASET_DIR}/output-{label}.json', 'r') as file:
            data = json.load(file)
        
        # Clean up the samples and create a DataFrame
        samples = [sample['response'].replace("<Transcript>", "").replace("</Transcript>", "").strip() for sample in data]
        df = pd.DataFrame({'Transcript': samples, 'Label': [label] * len(samples)})
        
        # Append each DataFrame to the list
        data_frames.append(df)
    
    # Concatenate all DataFrames into one
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df


def make_dataset(df, cols= ['Transcript', 'Label'], lable_name = 'Label'):
    df = df[cols]
    # Convert your data to Hugging Face's dataset format
    dataset = Dataset.from_pandas(df)

    # Define a mapping from labels to integers if not already done
    label2id = {label: idx for idx, label in enumerate(df[lable_name].unique())}
    id2label = {idx: label for label, idx in label2id.items()}

    # Add integer labels to the dataset
    dataset = dataset.map(lambda examples: {'label': label2id[examples[lable_name]]})
    unique_labels = set(dataset['label'])
    dataset = dataset.cast_column('label', ClassLabel(names=[str(label) for label in sorted(unique_labels)]))
    
    return dataset

def upload_to_gcs(bucket_name, source_dir, destination_dir):
    """Uploads a directory to the GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Recursively upload all files in the directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_file_path, source_dir)  # Get the relative path of the file
            blob_name = os.path.join(destination_dir, relative_path)  # Create destination path in GCS
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(source_file_path)
            print(f"File {source_file_path} uploaded to {blob_name}.")

def main(): # pragma: no cover
    # Ensure the local directory exists
    os.makedirs(LOCAL_DATASET_DIR, exist_ok=True)
    # Count elements in each file, save locally, and print results
    for file_path in file_paths:
        count = count_elements_and_save_locally(BUCKET_NAME, file_path, LOCAL_DATASET_DIR)
        if count is not None:
            print(f"{file_path}: {count} elements")
    # Create dataframe and dataset, save to disk and upload to GCS
    df = create_dataframe()
    dataset = make_dataset(df)
    dataset.save_to_disk('train_dataset_generated')
    upload_to_gcs(BUCKET_NAME, 'train_dataset_generated', 'train_dataset_generated')

if __name__ == "__main__":
    main()
