import os
import json
import traceback
from fastapi import APIRouter, HTTPException
from google.cloud import storage

# Define Router
router = APIRouter()

# GCP Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "innit_articles_bucket")  # Use environment variable for bucket name
DIAGNOSTIC_TEST_PATH = "generated_questions/diagnostic_test.json"  # Path in the GCP bucket

@router.get("/diagnostic")
async def get_diagnostic_test():
    """Fetch diagnostic test questions from GCP bucket."""
    try:
        # Initialize GCP Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(DIAGNOSTIC_TEST_PATH)
        
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Diagnostic test file not found.")

        # Load diagnostic test data
        diagnostic_data = json.loads(blob.download_as_text())
        return {"questions": diagnostic_data}
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching diagnostic test: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch diagnostic test data.")
