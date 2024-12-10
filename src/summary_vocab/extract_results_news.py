#%%#%%
import json
from google.cloud import storage
import re


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



# %%
def download_jsonl_from_gcp(bucket_name, directory_prefix, local_file_path):
    """
    Downloads a JSONL file from the folder starting with "prediction-model" that was created most recently in a GCP bucket.

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
    
    # Find the most recent folder starting with "prediction-model"
    latest_timestamp = None
    prediction_model_folder = None
    for blob in blobs:
        # Only consider blobs where the name starts with "prediction-model"
        if "prediction-model" in blob.name:
            # Compare the updated timestamp to find the most recent folder
            if latest_timestamp is None or blob.updated > latest_timestamp:
                latest_timestamp = blob.updated
                prediction_model_folder = blob.name
    
    if not prediction_model_folder:
        print("No folder starting with 'prediction-model' found.")
        return
    
    print(f"Found latest folder: {prediction_model_folder}")
    
    # Look for JSONL files within the folder
    for blob in blobs:
        if blob.name.startswith(prediction_model_folder) and blob.name.endswith(".jsonl"):
            print(f"Downloading {blob.name} to {local_file_path}...")
            blob.download_to_filename(local_file_path)
            print("Download complete.")
            return
    
    print(f"No JSONL file found in the folder '{prediction_model_folder}'.")


# %%
def upload_to_gcp(bucket_name, folder_prefix, file_name, data):
    """
    Uploads a dictionary as a JSON file to a GCP bucket.
    
    :param bucket_name: Name of the GCP bucket.
    :param folder_prefix: Folder path in the bucket where the file should be uploaded.
    :param file_name: Name of the file to be uploaded.
    :param data: Dictionary to be uploaded as a JSON file.
    """
    # Initialize the GCP client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Define the blob path (folder + filename)
    blob_path = f"{folder_prefix}/{file_name}.json"
    blob = bucket.blob(blob_path)

    # Convert dictionary to JSON string
    json_data = json.dumps(data, indent=4)

    # Upload JSON data to the bucket
    blob.upload_from_string(json_data, content_type="application/json")
    print(f"Uploaded to {blob_path}")


def main():
    news_local_file_path = NEWS_GCP_FILE_PATH.split("/")[1]
    read_json_from_gcp(BUCKET_NAME, NEWS_GCP_FILE_PATH, news_local_file_path)
    print(f"News article file downloaded to {news_local_file_path}")

    sum_local_file_path = 'summary_covab_news.jsonl'
    download_jsonl_from_gcp(BUCKET_NAME, NEWS_GCP_FILE_PATH.split("/")[0], sum_local_file_path)

    # Read news data from local
    data = []
    with open(news_local_file_path, 'r') as f:
        try:
            for line in f:
                data.append(json.loads(line))
        except json.JSONDecodeError:
            data = json.load(f)

    data_with_ids = [{"id": idx, **content} for idx, content in enumerate(data)]
    
    # Read and parse the file
    pred = []
    with open(sum_local_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            pred.append(json.loads(line))


    # Parse predictions and store them in a dictionary by ID
    pred_dict = {}
    for prediction in pred:
        try:
            request = prediction['request']['contents'][0]['parts'][0]['text']
            response = prediction['response']['candidates'][0]['content']['parts'][0]['text']
            # print(text)
            id_match = re.search(r"ID:\s*(\d+)", request)
            if id_match:
                item_id = int(id_match.group(1))
                pred_dict[item_id] = response
        except KeyError:
            print("Error processing prediction")

    # Reorder predictions to match the original input data
    reordered_predictions = [pred_dict.get(item['id'], None) for item in data_with_ids]

    for i, original_data in enumerate(data_with_ids):
        if reordered_predictions[i]:
            text = reordered_predictions[i]
            summary_match = re.search(r"<sum>\s*(.*?)\s*</sum>", text, re.DOTALL)
            vocab_match = re.search(r"<vocab>\s*(.*?)\s*</vocab>", text, re.DOTALL)
            question_match = re.search(r"<questions>\s*(.*?)\s*</questions>", text, re.DOTALL)

            if summary_match and vocab_match and question_match:
                original_data['summary'] = summary_match.group(1).strip()
                original_data['vocab'] = vocab_match.group(1).strip()
                original_data['questions'] = question_match.group(1).strip()
            else:
                print(f"Missing <sum>, <vocab> or <questions> for item {i}")
    
    # Iterate through the list of dictionaries and upload them
    for item in data_with_ids:
        try:
            # Extract the CEFR level (predictions) and Title
            level = item.get('predictions', 'unknown')
            title = item.get('Title', 'untitled').replace("/", "_").replace('\\', '_')  # Sanitize title to avoid path issues
            
            # Define the folder path in the bucket
            folder_path = f"bbc_news/{level}"

            # Upload the item to the bucket
            upload_to_gcp(BUCKET_NAME, folder_path, title, item)

        except Exception as e:
            print(f"Failed to upload item with ID {item.get('id')}: {e}")


if __name__ == "__main__":
    main() # pragma: no cover