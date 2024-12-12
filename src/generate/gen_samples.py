import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, GenerationConfig
import argparse
import os
from datasets import Dataset, load_from_disk
from google.cloud import storage
import json
import time
import random

# Setup the arguments for the trainer task
parser = argparse.ArgumentParser()
parser.add_argument(
    "--level", dest="level", required=True, type=str, choices=["A1", "A2", "B1", "B2", "C1"], help="Target level for the generated text"
)
parser.add_argument("--n_samples", dest="n_samples", default=10, type=int, help="Number of samples to generate")
args = parser.parse_args()

# Local directory to read the train dataset
LOCAL_DATASET_DIR = './datasets'
BUCKET_NAME = 'innit_articles_bucket'
GCS_OUTPUT_FILE_PATH = f"output-{args.level}.json"
BATCH_SIZE = 50  # Set the batch size for incremental saving

# Number of examples for few-shot learning
N_EXAMPLES = 5 
# Maximum length of the generated text
MAX_OUTPUT_TOKENS = 1000
TEMPERATURE = 0.5

# Project and model information
PROJECT_ID = "innit-437518"
REGION = 'us-central1'
MODEL_ID = 'gemini-1.5-flash-002'

LEVEL_LABEL_MAPPING = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4}

# Load train dataset
def load_datasets(local_dataset_dir):
    train_dataset_path = os.path.join(local_dataset_dir, 'train_dataset')
    if os.path.exists(train_dataset_path):
        train_dataset = load_from_disk(train_dataset_path)
        print("Successfully loaded datasets from disk")
        return train_dataset
    else:
        raise FileNotFoundError(
            f"Train dataset does not exist at '{train_dataset_path}'. Please run download_train_datasets.py first to download the data."
        )
    
train_dataset = load_datasets(LOCAL_DATASET_DIR)

# Get label
label = LEVEL_LABEL_MAPPING[args.level]
label_subset = train_dataset.filter(lambda example: example['label'] == label)

# Initialize Vertex AI client
vertexai.init(project=PROJECT_ID, location=REGION)

model = GenerativeModel(
    model_name=MODEL_ID,
    system_instruction=f"Generate English learning material (a transcript of video or audio) suitable for {args.level}-level learners. "
                      "Ensure the material is comparable in difficulty to the provided examples. "
                      "If the transcript is a dialogue, it should not contain additional contextual phrases or commentary. "
                      "Please wrap the transcript using <Transcript> tags."
)

generation_config = GenerationConfig(temperature=TEMPERATURE, max_output_tokens=MAX_OUTPUT_TOKENS)
chat_session = model.start_chat()

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    response = chat.send_message(prompt, generation_config=generation_config)
    return response.text

def upload_to_gcs(bucket_name, destination_blob_name, data):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Download existing data if exists, and append new data
    if blob.exists():
        existing_data = json.loads(blob.download_as_text())
        existing_data.extend(data)
    else:
        existing_data = data
    
    blob.upload_from_string(json.dumps(existing_data, indent=4), content_type='application/json')
    print(f"Data uploaded to gs://{bucket_name}/{destination_blob_name}")

# Prepare to collect output data in batches
batch_data = []

for i in range(args.n_samples):
    shuffled_subset = label_subset.shuffle(seed=42 + i)
    random_samples = shuffled_subset.select(range(N_EXAMPLES))
    transcripts = random_samples['Transcript']
    
    # Generate a new prompt with updated examples
    prompt = ""
    for j, example in enumerate(transcripts, start=1):
        prompt += f"Example {j}:\n{example}\n\n"
    
    # Get the response and add to batch data, retrying on failure
    try:
        response = get_chat_response(chat_session, prompt)
    except Exception as e:
        print(f"Failed to get response for sample {i+1} after retries: {e}")
        continue  # Skip this iteration if all retries fail

    batch_data.append({"prompt": prompt, "response": response})

    # Save and upload every BATCH_SIZE samples
    if (i + 1) % BATCH_SIZE == 0:
        upload_to_gcs(BUCKET_NAME, GCS_OUTPUT_FILE_PATH, batch_data)
        print(f"Progress: {i + 1}/{args.n_samples} samples generated and uploaded.")
        batch_data = []  # Clear batch data after upload

    time.sleep(random.uniform(4, 7))  # To avoid rate limiting

# Upload any remaining samples
if batch_data:
    upload_to_gcs(BUCKET_NAME, GCS_OUTPUT_FILE_PATH, batch_data)
    print(f"Final batch uploaded. Total: {args.n_samples} samples generated.")
