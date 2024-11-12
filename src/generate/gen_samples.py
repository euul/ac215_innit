import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, GenerationConfig
import argparse
import os
import asyncio
import aiohttp
from datasets import load_from_disk
from google.cloud import storage
import json
import time
from random import uniform

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

# Initialize Vertex AI client and model
vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel(model_name=MODEL_ID)

generation_config = GenerationConfig(temperature=TEMPERATURE, max_output_tokens=MAX_OUTPUT_TOKENS)

# Load datasets and filter by label
def load_datasets(local_dataset_dir):
    train_dataset_path = os.path.join(local_dataset_dir, 'train_dataset')
    if os.path.exists(train_dataset_path):
        train_dataset = load_from_disk(train_dataset_path)
        print("Successfully loaded datasets from disk")
        return train_dataset
    else:
        raise FileNotFoundError(f"Train dataset does not exist at '{train_dataset_path}'. Please run download_train_datasets.py first to download the data.")

train_dataset = load_datasets(LOCAL_DATASET_DIR)
label = LEVEL_LABEL_MAPPING[args.level]
label_subset = train_dataset.filter(lambda example: example['label'] == label)

async def async_get_chat_response(chat: ChatSession, prompt: str) -> str:
    """Asynchronously get the chat response with retries and exponential backoff."""
    max_retries = 5
    backoff = 1
    for attempt in range(max_retries):
        try:
            response = chat.send_message(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Max retries reached for prompt. Error: {e}")
                return None
            print(f"Retrying due to error: {e}. Attempt {attempt + 1}")
            await asyncio.sleep(backoff)
            backoff *= 2

def generate_prompt(samples):
    """Generate a prompt based on a set of samples."""
    prompt = ""
    for j, example in enumerate(samples, start=1):
        prompt += f"Example {j}:\n{example}\n\n"
    return prompt

async def process_sample(chat_session, sample_index, subset):
    """Process a single sample by generating a prompt and obtaining a response."""
    random_samples = subset.shuffle(seed=42 + sample_index).select(range(N_EXAMPLES))
    transcripts = random_samples['Transcript']
    prompt = generate_prompt(transcripts)
    response_text = await async_get_chat_response(chat_session, prompt)
    return {"prompt": prompt, "response": response_text} if response_text else None

async def gather_responses(subset, n_samples):
    """Generate responses asynchronously for all samples."""
    chat_session = model.start_chat()
    tasks = [process_sample(chat_session, i, subset) for i in range(n_samples)]
    responses = await asyncio.gather(*tasks)
    return [response for response in responses if response]

def upload_to_gcs(bucket_name, destination_blob_name, data):
    """Uploads data to GCS as a JSON file."""
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

async def main():
    # Get responses asynchronously and save them in batches
    all_responses = await gather_responses(label_subset, args.n_samples)
    batch_data = []
    
    for i, response in enumerate(all_responses, start=1):
        batch_data.append(response)
        if i % BATCH_SIZE == 0:
            upload_to_gcs(BUCKET_NAME, GCS_OUTPUT_FILE_PATH, batch_data)
            print(f"Uploaded batch of {BATCH_SIZE} samples to GCS.")
            batch_data = []

    # Upload any remaining responses
    if batch_data:
        upload_to_gcs(BUCKET_NAME, GCS_OUTPUT_FILE_PATH, batch_data)
        print(f"Final batch uploaded. Total: {args.n_samples} samples generated.")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
