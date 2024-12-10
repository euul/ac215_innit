from google.cloud import storage
import json
import random

# Configuration
BUCKET_NAME = 'innit_articles_bucket'
PROJECT_ID = "innit-437518"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]
GCS_FOLDER = "generated_questions/"
TEST_OUTPUT_FILE = "diagnostic_test.json"

# Initialize the Google Cloud Storage client
def get_gcp_client():
    return storage.Client(project=PROJECT_ID)

# Function to fetch and parse JSON files from GCP
def fetch_questions_from_gcp(client, level):
    bucket = client.get_bucket(BUCKET_NAME)
    blob_name = f"{GCS_FOLDER}generated_questions_{level}.json"
    blob = bucket.blob(blob_name)

    if not blob.exists():
        raise FileNotFoundError(f"The file {blob_name} does not exist in bucket {BUCKET_NAME}.")
    
    questions_data = blob.download_as_text()
    return json.loads(questions_data)

# Function to upload the combined test to GCP
def upload_to_gcp(client, data, destination_blob_name):
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # Upload JSON data
    blob.upload_from_string(
        data=json.dumps(data, indent=4),
        content_type='application/json'
    )
    print(f"File uploaded to gs://{BUCKET_NAME}/{destination_blob_name}")

# Main function
def main():
    client = get_gcp_client()
    combined_test = []

    for level in LEVELS:
        print(f"Processing level {level}...")
        try:
            # Fetch questions for the level
            questions = fetch_questions_from_gcp(client, level)

            # Randomly select 2 questions
            selected_questions = random.sample(questions, 2)

            # Append to the combined test
            combined_test.extend(selected_questions)

        except Exception as e:
            print(f"Error processing level {level}: {e}")

    # Upload the combined test to GCP
    upload_to_gcp(client, combined_test, f"{GCS_FOLDER}{TEST_OUTPUT_FILE}")

# Entry point
if __name__ == "__main__":
    main()
