import pandas as pd
from google.cloud import storage

# Convert DataFrame to JSON and save locally
def save_df_to_json(df, json_file_path):
    """
    Save a DataFrame to a JSON file.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        json_file_path (str): Path to save the JSON file.
    """
    df.to_json(json_file_path, orient='records', lines=True)
    print(f"DataFrame saved as JSON to {json_file_path}")

# Upload JSON file to GCP
def upload_json_to_gcp(bucket_name, destination_blob_name, json_file_path):
    """
    Upload a JSON file to a GCP bucket.
    
    Args:
        bucket_name (str): Name of the GCP bucket.
        destination_blob_name (str): Destination path in the bucket.
        json_file_path (str): Local path of the JSON file to upload.
    """
    # Initialize GCP Storage client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload the file
    blob.upload_from_filename(json_file_path)
    print(f"Uploaded {json_file_path} to {bucket_name}/{destination_blob_name}")


def main(): # pragma: no cover
    # Example DataFrame
    df = pd.read_csv('bbc_news_articles.csv')
    # Remove null values (if any)
    df = df.dropna()

    # Define paths and bucket details
    json_file_path = "bbc_news_articles.json"
    bucket_name = 'innit_articles_bucket'
    destination_blob_name = "bbc_news_articles.json"

    # Save DataFrame as JSON
    save_df_to_json(df, json_file_path)

    # Upload JSON to GCP bucket
    upload_json_to_gcp(bucket_name, destination_blob_name, json_file_path)

if __name__ == "__main__":
    main() # pragma: no cover