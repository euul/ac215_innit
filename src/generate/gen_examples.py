import json
import os
from google.cloud import storage
from datasets import load_dataset
import requests
import google.generativeai as genai


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

def generate_one_synthetic_text(entry, api_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    original_text = entry['text']  # Existing text from dataset
    difficulty_level = entry['label'] 
        
    # Define prompts using both the original text and the difficulty level
    if difficulty_level == "A1":
        prompt = f"Use the following example to generate a very simple text for any topic of your choosing, suitable for a beginner reader: '{original_text}'"
    elif difficulty_level == "A2":
        prompt = f"Use the following example to generate a text for any topic of your choosing, suitable for elementary readers: '{original_text}'"
    elif difficulty_level == "B1":
        prompt = f"Use the following example to generate a moderately complex text, suitable for intermediate readers: '{original_text}'"
    elif difficulty_level == "B2":
        prompt = f"Use the following example to generate a vocabulary-rich text, suitable for upper-intermediate readers: '{original_text}'"
    elif difficulty_level == "C1":
        prompt = f"Use the following example to generate a  complex, vocabulary-rich texts. suitable for an advanced reader: '{original_text}'"

    # Define the payload for the API request
    payload = {
        "model": "gemini-1.5-flash",
        "prompt": prompt
    }

    # Send a POST request to the API
    response = requests.post(api_url, headers=headers, json=payload)
    response_data = response.json()
        
    # Get the generated text from the response
    generated_text = response_data.get("text", "")
    
    return ({"generated_text": generated_text, "label": difficulty_level})


# def generate_synthetic_texts(dataset, api_url, api_key):
#     synthetic_data = []
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
    
#     for entry in dataset:
#         original_text = entry['text']  
#         difficulty_level = entry['label']
        
#         # Define prompts using both the original text and the difficulty level
#         if difficulty_level == "A1":
#             prompt = f"Use the following example to generate a very simple text for any topic of your choosing, suitable for a beginner reader: '{original_text}'"
#         elif difficulty_level == "A2":
#             prompt = f"Use the following example to generate a text for any topic of your choosing, suitable for elementary readers: '{original_text}'"
#         elif difficulty_level == "B1":
#             prompt = f"Use the following example to generate a moderately complex text, suitable for intermediate readers: '{original_text}'"
#         elif difficulty_level == "B2":
#             prompt = f"Use the following example to generate a vocabulary-rich text, suitable for upper-intermediate readers: '{original_text}'"
#         elif difficulty_level == "C1":
#             prompt = f"Use the following example to generate a  complex, vocabulary-rich texts. suitable for an advanced reader: '{original_text}'"

#         # Define the payload for the API request
#         payload = {
#             "model": "gemini-1.5-flash",
#             "prompt": prompt
#         }

#         # Send a POST request to the API
#         response = requests.post(api_url, headers=headers, json=payload)
#         response_data = response.json()
        
#         # Get the generated text from the response
#         generated_text = response_data.get("text", "")
#         synthetic_data.append({"generated_text": generated_text, "label": difficulty_level})

#     return synthetic_data



BUCKET_NAME = 'innit_articles_bucket'
TRAIN_BLOB_PREFIX = 'train_dataset/'
LOCAL_DATASET_DIR = './datasets'

download_dataset_folder(BUCKET_NAME, TRAIN_BLOB_PREFIX, LOCAL_DATASET_DIR)

with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS']) as f:
    service_account_info = json.load(f)
    api_key = service_account_info.get("api_key")

genai.configure(api_key=api_key)
api_url = "what goes here?"  #
model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(
#     "Tell me a story about a magic backpack.",
#     generation_config=genai.types.GenerationConfig(
#         # Only one candidate for now.
#         candidate_count=1,
#         max_output_tokens=800,
#         temperature=1.0,
#     )
# )

#single example test
entry = {
    "text": """
    Hello and good morning! Well, we're off to a good start in the south this week, as most of the rain from the weekend has disappeared – just a few patches of cloud and maybe some showers here on the east coast. They'll all clear up by lunchtime, though. Over the next day or so, London and the area around Kent can expect a couple of isolated showers, but mostly dry through until Thursday.

    It's not such good news for the north-west this week, I'm afraid: more wet weather, and not a lot of sunshine. Some of today's showers will be heavy – and even thundery in Manchester and across the Pennines. Leeds will escape the thunderstorms, with drizzle and light rain only throughout the rest of the day and tonight.

    Elsewhere it becomes dry today, but with some foggy patches towards Wales. In England, tomorrow morning will see a dry, bright start in most places, with high temperatures throughout the week. We might see one or two thunderstorms appearing as the week goes on, with temperatures everywhere at 29 to 30 degrees. 

    By the weekend, unfortunately, the dry weather will make way for mostly cloudy skies and rain. The rain will move from Scotland, down towards the north and reach the south coast by Saturday afternoon. Temperatures, at least, will stay mostly warm at around 21 degrees for the weekend. It might feel like a nice change from the high twenties and early thirties we'll see in the week. That's all from me until tomorrow. Enjoy the mini-heatwave while you can!
    """,
    "label": "B1" 
}

synthetic_text = generate_one_synthetic_text(entry, api_url, api_key)
print("Generated Synthetic Text:", synthetic_text["generated_text"])
print("Label:", synthetic_text["label"])