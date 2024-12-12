#%%#%%
import json
from google.cloud import storage
import re
import os


BUCKET_NAME = "innit_articles_bucket"
MODULE_BLOB_NAME = "yt_transcripts"
LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']

#%%
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/text-generator.json"
# %%
# read original data from GCP
def read_json_from_gcp():
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for level in LEVELS:
        prefix = MODULE_BLOB_NAME + '/' + level
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        for blob in blobs:
            if blob.name.endswith(".json"):
                # Ensure that the directory structure exists locally
                local_dir = os.path.dirname(blob.name)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)  # Create the directory if it doesn't exist

                # Download the file to the local system
                blob.download_to_filename(blob.name)

        print(f"Files downloaded to {prefix}")

# download the summarization and vocab files from GCP
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

# %%
def read_predictions_from_jsonl(local_file_path):
    """
    Reads predictions from a JSONL file.

    :param local_file_path: Path to the JSONL file.
    :return: List of predictions.
    """
    pred = []
    with open(local_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            pred.append(json.loads(line))

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
    return pred_dict

# %%
def update_local_json(mapping_file_path, pred_dict):
    with open(mapping_file_path, 'r') as f:
        id_mapping = json.load(f)

    for key in id_mapping.keys():
        id = int(key)
        file_name = id_mapping[key]
        file_path = f"{MODULE_BLOB_NAME}/{level}/{file_name}"

        if pred_dict[id]:
            remove_file = False
            # get original json file
            with open(file_path, 'r') as f:
                original_data = json.load(f)
            
            # get summary and vocab from prediction
            text = pred_dict[id]
            summary_match = re.search(r"<sum>\s*(.*?)\s*</sum>", text, re.DOTALL)
            vocab_match = re.search(r"<vocab>\s*(.*?)\s*</vocab>", text, re.DOTALL)
            questions_match = re.search(r"<questions>\s*(.*?)\s*</questions>", text, re.DOTALL)

            # add summary and vocab to original data
            if summary_match and vocab_match and questions_match:
                original_data['id'] = id
                original_data['summary'] = summary_match.group(1).strip()
                original_data['vocab'] = vocab_match.group(1).strip()
                original_data['questions'] = questions_match.group(1).strip()
            else:
                remove_file = True
                print(f"Missing <sum>, <vocab>, or <questions> for item {id}")

            # save the updated data locally
            with open(file_path, 'w') as f:
                json.dump(original_data, f, indent=4)

        # if id not in pred_dict, delete the local file
        else:
            remove_file = True
            print(f"Missing prediction for item {id}")
        
        if remove_file:
            os.remove(file_path)
            print('Removed file:', file_path)

def upload_and_sync_selected_folders(bucket_name, local_base_folder, folders_to_sync, bucket_base_folder=""):
    """
    Sync specific folders from the local directory to a GCP bucket,
    always overwriting files in the bucket.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Iterate through each folder to sync
    for folder in folders_to_sync:
        local_folder = os.path.join(local_base_folder, folder)
        bucket_folder = os.path.join(bucket_base_folder, folder)

        # List existing files in the specific bucket folder
        existing_files = {blob.name for blob in bucket.list_blobs(prefix=bucket_folder)}

        # Upload files from the local folder
        for root, _, files in os.walk(local_folder):
            for file_name in files:
                local_file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(local_file_path, local_base_folder)
                gcp_blob_path = os.path.join(bucket_base_folder, relative_path)

                blob = bucket.blob(gcp_blob_path)
                print(f"Uploading: {gcp_blob_path}")
                blob.upload_from_filename(local_file_path)

        # Delete files in the bucket folder that are not present locally
        for blob_name in existing_files:
            relative_path = os.path.relpath(blob_name, bucket_base_folder)
            local_file_path = os.path.join(local_base_folder, relative_path)
            if not os.path.exists(local_file_path):
                print(f"Deleting: {blob_name}")
                bucket.blob(blob_name).delete()


# %%

def main(): # pragma: no cover
    read_json_from_gcp()

    for level in LEVELS:
        directory_prefix = f"{MODULE_BLOB_NAME}/{level}"
        local_file_path = f"{MODULE_BLOB_NAME}/{level}/summary_vocab.jsonl"
        mapping_file_path = f"{MODULE_BLOB_NAME}/{level}/id_mapping.json"

        download_jsonl_from_gcp(BUCKET_NAME, directory_prefix, local_file_path)
        # Check if both paths are valid
        if os.path.exists(local_file_path) and os.path.exists(mapping_file_path):
            pred_dict = read_predictions_from_jsonl(local_file_path)
            update_local_json(mapping_file_path, pred_dict)
        else:
            print(f"Skipping level '{level}': Missing file(s).")

    upload_and_sync_selected_folders(BUCKET_NAME, MODULE_BLOB_NAME, LEVELS, MODULE_BLOB_NAME)

if __name__ == "__main__":
    main() # pragma: no cover
