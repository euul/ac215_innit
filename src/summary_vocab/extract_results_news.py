#%%#%%
import json
from google.cloud import storage
import re
from collections import defaultdict


BUCKET_NAME = "innit_articles_bucket"
NEWS_GCP_FILE_PATH = "bbc_news/bbc_news_articles_labeled.json"

#%%
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/text-generator.json"

# %%
def read_json_from_gcp(bucket_name, input_file_path, local_file_path):
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    # Get the blob (file)
    blob = bucket.blob(input_file_path)
   # Download the file to the local system
    blob.download_to_filename(local_file_path)

news_local_file_path = NEWS_GCP_FILE_PATH.split("/")[1]
read_json_from_gcp(BUCKET_NAME, NEWS_GCP_FILE_PATH, news_local_file_path)
print(f"News article file downloaded to {news_local_file_path}")

# %%
def download_jsonl_from_gcp(bucket_name, directory_prefix, local_file_path):
    """
    Downloads a JSONL file from a folder starting with "prediction-model" in a GCP bucket.

    :param bucket_name: Name of the GCP bucket.
    :param directory_prefix: Prefix to look for folders in the bucket.
    :param local_file_path: Path to save the downloaded file locally.
    """
    # Initialize the GCP client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # List blobs (files) in the bucket
    blobs = list(bucket.list_blobs(prefix=directory_prefix))
    
    # Find the folder starting with "prediction-model"
    prediction_model_folder = None
    for blob in blobs:
        # Get the folder name (e.g., "bbc_news/prediction-model-folder/")
        if "prediction-model" in blob.name:
            prediction_model_folder = blob.name
            break
    
    if not prediction_model_folder:
        print("No folder starting with 'prediction-model' found.")
        return
    
    print(f"Found folder: {prediction_model_folder}")
    
    # Look for JSONL files within the folder
    for blob in blobs:
        if blob.name.startswith(prediction_model_folder) and blob.name.endswith(".jsonl"):
            print(f"Downloading {blob.name} to {local_file_path}...")
            blob.download_to_filename(local_file_path)
            print("Download complete.")
            return
    
    print(f"No JSONL file found in the folder '{prediction_model_folder}'.")


sum_local_file_path = 'summary_covab_news.jsonl'
download_jsonl_from_gcp(BUCKET_NAME, NEWS_GCP_FILE_PATH.split("/")[0], sum_local_file_path)

#%%
# Read and parse the file
pred = []
with open(sum_local_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        pred.append(json.loads(line))

# print(pred[0]['response']['candidates'][0]['content']['parts'][0]['text'])

# %%
# Read news data from local
data = []
with open(news_local_file_path, 'r') as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        for line in f:
            data.append(json.loads(line))

# %%
# Group valid data by 'prediction'
grouped_data = defaultdict(list)

for i in range(len(data)):
    text = pred[i]['response']['candidates'][0]['content']['parts'][0]['text']
    
    # Extract <sum> and <vocab> content using regex
    summary_match = re.search(r"<sum>\s*(.*?)\s*</sum>", text, re.DOTALL)
    vocab_match = re.search(r"<vocab>\s*(.*?)\s*</vocab>", text, re.DOTALL)
    
    # Only add items with both <sum> and <vocab> to the grouped_data dictionary
    if summary_match and vocab_match:
        valid_item = data[i].copy()
        valid_item['summary'] = summary_match.group(1).strip()
        valid_item['vocab'] = vocab_match.group(1).strip()
        
        # Group items by their 'prediction' value
        prediction = valid_item.get('predictions', 'unknown')
        grouped_data[prediction].append(valid_item)
    else:
        print(f"Skipping item {i} due to missing <sum> or <vocab>")

# %%
# Save each group to a separate file
for prediction, items in grouped_data.items():
    # Create file name based on prediction value
    file_name = f"{news_local_file_path}_{prediction}.json"
    
    # Save grouped items to the file
    with open(file_name, "w") as f:
        json.dump(items, f, indent=4)
    
    print(f"Data for prediction '{prediction}' saved to {file_name}")

# %%
def upload_to_gcp(bucket_name, destination_blob_name, source_file_name):
    """
    Uploads a file to the specified GCP bucket.
    
    :param bucket_name: GCP bucket name
    :param destination_blob_name: Destination path in the bucket
    :param source_file_name: Local file path to upload
    """
    # Initialize the GCP client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob for the destination file
    blob = bucket.blob(destination_blob_name)
    
    # Upload the file
    blob.upload_from_filename(source_file_name)
    print(f"File uploaded to {destination_blob_name} in bucket {bucket_name}.")


#%%
# Call the function to upload
upload_to_gcp(BUCKET_NAME, NEWS_GCP_FILE_PATH, news_local_file_path)

for prediction, items in grouped_data.items():
    # Create file name based on prediction value
    local_file_name = f"{news_local_file_path}_{prediction}.json"
    gcp_file_path = NEWS_GCP_FILE_PATH.split("/")[0] + '/' + local_file_name
    upload_to_gcp(BUCKET_NAME, gcp_file_path, file_name)
