from google.cloud import storage
import os

# Configuration
BUCKET_NAME = 'innit_articles_bucket'
PROJECT_ID = "innit-437518"
LOCAL_FOLDER = "./generated_questions"
GCS_FOLDER = "generated_questions/"  # Folder in the bucket


def upload_files_to_gcp():
    """Uploads JSON files from the local folder to the specified GCP bucket."""
    # Initialize the Google Cloud Storage client
    client = storage.Client(project=PROJECT_ID)

    # Get the bucket
    bucket = client.get_bucket(BUCKET_NAME)

    # Upload JSON files to the bucket
    for file_name in os.listdir(LOCAL_FOLDER):
        if file_name.endswith(".json"):  # Only process JSON files
            local_file_path = os.path.join(LOCAL_FOLDER, file_name)
            blob_name = os.path.join(GCS_FOLDER, file_name)  # Define the blob name (path in GCS)

            # Create a new blob and upload the file's contents
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_file_path)

            print(f"Uploaded {file_name} to gs://{BUCKET_NAME}/{blob_name}")

    print("All files uploaded successfully.")


def main():
    """Main function to execute the upload process."""
    upload_files_to_gcp()


if __name__ == "__main__":
    main()
