import json
from fastapi import APIRouter
from google.cloud import storage

router = APIRouter()

GCP_BUCKET_NAME = "innit_articles_bucket"  # Replace with your bucket name
DIAGNOSTIC_TEST_PATH = "generated_questions/diagnostic_test.json"  # Path in the GCP bucket

@router.get("/diagnostic-test")
def get_diagnostic_test():
    """Fetch diagnostic test questions from GCP bucket."""
    try:
        # Initialize GCP Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(DIAGNOSTIC_TEST_PATH)
        
        if not blob.exists():
            return {"error": "Diagnostic test file not found."}

        # Load diagnostic test data
        diagnostic_data = json.loads(blob.download_as_text())
        return {"questions": diagnostic_data}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
