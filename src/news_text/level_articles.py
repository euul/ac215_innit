import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" # disable GPU for testing
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
from google.cloud import storage
import os
import json
import pandas as pd


BUCKET_NAME = 'innit_articles_bucket'
BLOB_NAME = 'distill_bert_a1_weights.pth'
LOCAL_MODEL_PATH = './distill_bert_a1_weights.pth'
NUM_LABELS = 5

ARTICLE_DIR = 'bbc_news/bbc_news_articles.json'
ARTICLE_LABELED_DIR = 'bbc_news/bbc_news_articles_labeled.json'

LABEL_MAPPING = {
    0: "A1",
    1: "A2",
    2: "B1",
    3: "B2",
    4: "C1"
}


def download_json_from_gcp(bucket_name, blob_name, local_file_path):
    """Download a JSON file from a GCP bucket."""
    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Download the blob to the local file
    blob.download_to_filename(local_file_path)
    print(f"Downloaded '{blob_name}' from bucket '{bucket_name}' to '{local_file_path}'.")


def convert_json_to_hf_dataset(local_file_path):
    """Convert the downloaded JSON file into a Hugging Face Dataset."""
    data = []
    with open(local_file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    # Ensure the data is a list of dictionaries for Hugging Face compatibility
    if isinstance(data, dict):
        data = [data]
    
    hf_dataset = Dataset.from_list(data)
    print("Converted JSON data to Hugging Face Dataset.")
    return hf_dataset


def download_weights(bucket_name, blob_name, local_model_path):
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


# Modify the dataset and map the predictions
def infer(model, dataset):
    tokenizer = AutoTokenizer.from_pretrained("deberta-v3-small")

    # Tokenize the dataset
    tokenized_dataset = dataset.map(
        lambda examples: tokenizer(examples['Text'], truncation=True, padding='max_length', max_length=800),
        batched=True
    )

    # Convert to PyTorch tensors
    input_ids = torch.tensor(tokenized_dataset['input_ids'])
    attention_mask = torch.tensor(tokenized_dataset['attention_mask'])

    # Make predictions
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)

    # Convert numerical predictions to alphabet labels
    label_predictions = [LABEL_MAPPING[pred.item()] for pred in predictions]

    # Add predictions as a new column to the dataset
    dataset = dataset.add_column("predictions", label_predictions)

    return dataset


def upload_predictions_to_gcp_json(dataset, bucket_name, filename, temp_file="temp_predictions.json"):
    """
    Convert a Hugging Face Dataset to JSON and upload it to a GCP bucket.
    """
    # Convert Hugging Face dataset to Pandas DataFrame
    dataset_df = pd.DataFrame(dataset)

    # Save DataFrame to a local JSON file
    dataset_df.to_json(temp_file, orient="records", lines=True)
    print(f"Saved dataset to temporary file: {temp_file}")

    # Upload the JSON file to GCP
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(temp_file)
    print(f"Uploaded '{filename}' to GCP bucket '{bucket_name}'")

    # Clean up the temporary file
    os.remove(temp_file)
    print(f"Deleted temporary file: {temp_file}")
    

def main(): # pragma: no cover
    # Download article data from GCP, convert to HF dataset
    download_json_from_gcp(BUCKET_NAME, ARTICLE_DIR, ARTICLE_DIR)
    hf_dataset = convert_json_to_hf_dataset(ARTICLE_DIR)
    # Load the model
    download_weights(BUCKET_NAME, BLOB_NAME, LOCAL_MODEL_PATH)
    num_labels = NUM_LABELS
    model = load_model(LOCAL_MODEL_PATH, num_labels)
    # Make predictions
    predictions = infer(model, hf_dataset)
    # Upload the labeled data back to GCP
    upload_predictions_to_gcp_json(predictions, BUCKET_NAME, ARTICLE_LABELED_DIR)


if __name__ == "__main__":
    main() # pragma: no cover