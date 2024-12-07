from fastapi import APIRouter, HTTPException
from ..utils.media_manager import MediaManager

# Initialize MediaManager
media_manager = MediaManager(bucket_name="innit_articles_bucket")

router = APIRouter()

@router.get("/transcripts")
def list_video_transcripts():
    """Fetch video transcripts."""
    try:
        transcripts = media_manager.get_video_transcripts()
        return {"transcripts": transcripts}
    except Exception as e:
        print(f"Error fetching video transcripts: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching video transcripts.")

@router.get("/articles")
def list_articles():
    """Fetch articles."""
    try:
        articles = media_manager.get_articles()
        return {"articles": articles}
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching articles.")
    
@router.get("/articles/{id}")
def get_article(id: str):
    """Fetch a specific article by ID."""
    try:
        article = media_manager.get_article_by_id(id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return {"article": article}
    except Exception as e:
        print(f"Error fetching article {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching article")

@router.get("/videos/{id}")
def get_video(id: str):
    """Fetch a specific video by ID."""
    try:
        video = media_manager.get_video_by_id(id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"video": video}
    except Exception as e:
        print(f"Error fetching video {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching video")