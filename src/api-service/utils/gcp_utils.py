from google.cloud import storage
import json

def get_video_transcripts_from_bucket(bucket_name):
    """Fetches video transcripts stored as JSON files in the GCP bucket's yt_transcripts folder."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="yt_transcripts/B2/")  # List files in the yt_transcripts folder

    transcripts = []
    for blob in blobs:
        if blob.name.endswith(".json"):  # Only process JSON files
            content = blob.download_as_text()  # Download JSON content as a string
            transcript = json.loads(content)  # Parse JSON content
            transcripts.append(transcript)  # Append parsed transcript to list

    return transcripts

def create_user_in_bucket(bucket_name, username, user_data):
    """Creates a new user in the GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"users/{username}.json")
    
    if blob.exists():
        raise Exception("User already exists.")
    
    blob.upload_from_string(json.dumps(user_data), content_type="application/json")

def get_user_from_bucket(bucket_name, username):
    """Fetches user data from the GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"users/{username}.json")
    
    if not blob.exists():
        return None
    
    content = blob.download_as_text()
    return json.loads(content)
