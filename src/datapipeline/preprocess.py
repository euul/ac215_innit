import os
import json
import pandas as pd
import torch
from torch.utils.data import DataLoader
from datasets import Dataset, ClassLabel
from google.cloud import storage 


def get_filepaths(directory):
    filepaths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepaths.append(os.path.join(root, file))
    return filepaths

def combine_jsons(directory = 'data/'):
    file_paths = [f for f in get_filepaths(directory) if f.endswith('.json')]
    dfs = []

    for file_path in file_paths:
        df_source = pd.read_json(file_path, lines=True)
        dfs.append(df_source)

    df = pd.concat(dfs, axis=0).reset_index(drop=True)
    return df

def data_clean(df, col_name, val_to_remove):
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' not found in the DataFrame.")
    
    if val_to_remove not in df[col_name].values:
        raise ValueError(f"Value '{val_to_remove}' not found in the column '{col_name}'.")
    
    df = df[df[col_name] != val_to_remove]
    # label_distribution = df[col_name].value_counts()
    # # Display the label distribution statistics
    # print(label_distribution)
    return df
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

def split_dataset(dataset, directory = 'app/data/', bucket_name = "innit_articles_bucket"):
    # Use Hugging Face's train_test_split to create train, validation, and test sets
    train_valid_split = dataset.train_test_split(test_size=0.4, stratify_by_column='label')  # 60% train, 40% temp (validation+test)

    valid_test_split = train_valid_split['test'].train_test_split(test_size=0.5, stratify_by_column='label')  # Split temp into 50% validation, 50% test

    # Combine into a final dataset dict
    train_dataset = train_valid_split['train']
    valid_dataset = valid_test_split['train']  # validation set
    test_dataset = valid_test_split['test']    # test set

    train_dataset.save_to_disk(directory + 'train_dataset')
    upload_to_gcs(bucket_name, directory + 'train_dataset', 'train_dataset')
    valid_dataset.save_to_disk(directory + 'valid_dataset')
    upload_to_gcs(bucket_name, directory + 'valid_dataset', 'valid_dataset')
    test_dataset.save_to_disk(directory + 'test_dataset')
    upload_to_gcs(bucket_name, directory + 'test_dataset', 'test_dataset')

    print(f'Train, Validation and Test datasets created and saved to GCP bucket')





df = combine_jsons()
df = data_clean(df,'Label', 'Level not found')
dataset = make_dataset(df)
split_dataset(dataset)