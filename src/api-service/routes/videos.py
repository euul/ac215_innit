import json
from fastapi import APIRouter
from utils.gcp_utils import get_video_transcripts_from_bucket, get_articles_from_bucket

router = APIRouter()

GCP_BUCKET_NAME = "innit_articles_bucket"  # Replace with your bucket name

@router.get("/transcripts")
def list_video_transcripts():
    """Fetch video transcripts from GCP bucket."""
    try:
        transcripts = get_video_transcripts_from_bucket(GCP_BUCKET_NAME)
        return {"transcripts": transcripts}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

@router.get("/articles")
def list_articles():
    """Fetch articles from GCP bucket."""
    try:
        articles = get_articles_from_bucket(GCP_BUCKET_NAME)
        return {"articles": articles}
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return {"error": str(e)}
