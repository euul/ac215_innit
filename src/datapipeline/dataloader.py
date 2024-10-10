import os
import pandas as pd
import json
from google.cloud import storage


def read_json_from_gcp(bucket_name, blob_name, save_path):
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    # Get the blob (file)
    blob = bucket.blob(blob_name)
    # Download the blob content as a strings
    json_data = blob.download_as_text()

    with open(save_path, 'w') as f:
        f.write(json_data)
    
    print(f"JSON data from {blob_name} saved to {save_path}")



bucket_name = 'innit_articles_bucket'
blob_names = ['scraped_all_content.json', 'scraped_all_content_teens.json'] 

for blob_name in blob_names:
    save_path = '/app/data/' + blob_name
    read_json_from_gcp(bucket_name, blob_name, save_path)


