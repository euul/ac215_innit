import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
from google.cloud import storage
import os
import json


BUCKET_NAME = 'innit_articles_bucket'
BLOB_NAME = 'distill_bert_c1_weights.pth'
LOCAL_MODEL_PATH = './distill_bert_c1_weights.pth'
NUM_LABELS = 5

TRANSCRIPT_DIR = './yt_transcripts'


def download_transcripts(bucket_name, folder_name, local_dir='./yt_transcripts'):
    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Ensure the local directory exists
    os.makedirs(local_dir, exist_ok=True)

    # List and download all files in the specified folder in the bucket
    blobs = bucket.list_blobs(prefix=f"{folder_name}/")
    for blob in blobs:
        # Skip if it's a folder (only download files)
        if not blob.name.endswith('/'):
            # Define the local path for the downloaded file
            local_file_path = os.path.join(local_dir, os.path.basename(blob.name))
            # Download the file
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {blob.name} to {local_file_path}")

    print("All transcripts downloaded successfully.")

class TranscriptDataset(Dataset):
    def __init__(self, transcript_dir = TRANSCRIPT_DIR, transcript_col = "transcript"):
        self.transcript_dir = transcript_dir
        self.transcript_col = transcript_col
        self.files = []
        self.texts = []

        for filename in os.listdir(transcript_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(transcript_dir, filename)
            with open(filepath, 'r') as f:
                json_data = json.load(f)

                if transcript_col in json_data and json_data[transcript_col]:
                        joined_text = " ".join(
                            entry["text"] for entry in json_data[transcript_col] if "text" in entry
                        )
                        self.files.append(filepath)
                        self.texts.append(joined_text)

    
    def to_hf_dataset(self):
        return Dataset.from_dict({"Transcript": self.texts, "file_path": self.files})
    
    def __iter__(self):
        for filepath, text in zip(self.files, self.texts):
            yield filepath, text




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


def infer(model, tokenizer, text):
    """
    Perform inference on a single transcript.
    
    Args:
        model: The pre-trained model.
        tokenizer: The tokenizer corresponding to the model.
        text: The transcript text to classify.
    
    Returns:
        prediction: The predicted label index.
    """
    # Tokenize the transcript
    tokenized_input = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=800,
        return_tensors="pt"
    )

    input_ids = tokenized_input["input_ids"]
    attention_mask = tokenized_input["attention_mask"]

    # Perform inference
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()  # Get the predicted label index

    return prediction


def update_json_files_with_labels(predictions_with_files):
    # Define the label mapping
    LABEL_MAPPING = {
        0: "A1",
        1: "A2",
        2: "B1",
        3: "B2",
        4: "C1"
    }

    for file_path, label_id in predictions_with_files:
        # Map the numeric label to the readable label
        label = LABEL_MAPPING.get(label_id, "Unknown")  # Default to "Unknown" otherwise

        # Read the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Add or update the label in the JSON data
        data['label'] = label

        # Write the updated data back to the file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Updated {file_path} with label '{label}'")

def upload_to_gcp_bucket(bucket_name, local_folder, predictions_with_files):
    # Initialize the GCP client
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    # Define the label mapping (same as in `update_json_files_with_labels`)
    LABEL_MAPPING = {
        0: "A1",
        1: "A2",
        2: "B1",
        3: "B2",
        4: "C1"
    }

    # Upload each JSON file to its respective label folder
    for file_path, label_id in predictions_with_files:
        # Map the numeric label to the readable label
        label = LABEL_MAPPING.get(label_id, "Unknown")  # Default to "Unknown" otherwise

        # Ensure the label is valid
        if label == "Unknown":
            print(f"Skipping file {file_path} due to unknown label.")
            continue

        # Get the filename from the file path
        filename = os.path.basename(file_path)

        # Define the blob path in the bucket (e.g., yt_transcripts/A1/filename.json)
        blob_path = f"yt_transcripts/{label}/{filename}"
        blob = bucket.blob(blob_path)

        # Upload the file to the GCP bucket
        blob.upload_from_filename(file_path, content_type='application/json')
        print(f"Uploaded '{filename}' to GCP bucket '{bucket_name}' in folder '{label}'")


def main():  # pragma: no cover
    # Step 1: Download transcripts from the GCP bucket
    download_transcripts(BUCKET_NAME, "yt_transcripts")
    
    # Step 2: Initialize the dataset
    dataset = TranscriptDataset()

    # Step 3: Download model weights
    download_weights(BUCKET_NAME, BLOB_NAME, LOCAL_MODEL_PATH)

    # Step 4: Load the model and tokenizer
    model = load_model(LOCAL_MODEL_PATH, NUM_LABELS)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small")

    # Step 5: Iterate over each transcript in the dataset
    for file_path, text in dataset:
        print(f"Processing file: {file_path}")

        # Perform inference using the refactored `infer` function
        prediction = infer(model, tokenizer, text)

        # Update the JSON file with the label
        update_json_files_with_labels([(file_path, prediction)])

        # Upload the updated file to the GCP bucket
        upload_to_gcp_bucket(BUCKET_NAME, TRANSCRIPT_DIR, [(file_path, prediction)])

    print("Processing completed for all files.")


if __name__ == "__main__":
    main()
