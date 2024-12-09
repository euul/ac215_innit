from fastapi import APIRouter, HTTPException
from ..utils.media_manager import MediaManager
from ..utils.user_manager import UserManager

# Initialize MediaManager
media_manager = MediaManager(bucket_name="innit_articles_bucket")
user_manager = UserManager(bucket_name="innit_articles_bucket")

router = APIRouter()

@router.get("/transcripts")
def list_video_transcripts(username: str):
    """Fetch video transcripts based on the user's level."""
    try:
        # Fetch user metadata to determine the level
        user_metadata = user_manager.get_metadata(username)  # Assuming you have this method
        user_level = user_metadata.get("level", "B2")  # Default to B2 if no level is set
        
        # Fetch transcripts based on the user's level
        transcripts = media_manager.get_video_transcripts(level=user_level)
        return {"transcripts": transcripts}
    except Exception as e:
        print(f"Error fetching video transcripts: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching video transcripts.")

@router.get("/articles")
def list_articles(username: str):
    """Fetch articles based on the user's level."""
    try:
        # Fetch user metadata to determine the level
        user_metadata = user_manager.get_metadata(username)  # Assuming you have this method
        user_level = user_metadata.get("level", "B2")  # Default to B2 if no level is set
        
        # Fetch articles based on the user's level
        articles = media_manager.get_articles(level=user_level)
        return {"articles": articles}
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching articles.")

    
from fastapi import HTTPException, Request

def get_authenticated_user(request: Request):
    username = request.headers.get("X-Username")
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized: Username not found in headers")
    return username

from fastapi import Depends

@router.get("/articles/{id}")
def get_article(id: str, username: str = Depends(get_authenticated_user)):
    """
    Fetch a specific article by ID.
    Validate the user's level before providing access.
    """
    try:
        # Fetch the user's level from the database or metadata
        user_metadata = user_manager.get_metadata(username)
        user_level = user_metadata.get("level", "NA")

        # Fetch the article based on the user's level
        article = media_manager.get_article_by_id(id, user_level)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return {"article": article}
    except Exception as e:
        print(f"Error fetching article {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching article")

@router.get("/videos/{id}")
def get_video(id: str, username: str = Depends(get_authenticated_user)):
    """
    Fetch a specific video by ID.
    Validate the user's level before providing access.
    """
    try:
        # Fetch the user's level from the database or metadata
        user_metadata = user_manager.get_metadata(username)
        user_level = user_metadata.get("level", "NA")

        # Fetch the video based on the user's level
        video = media_manager.get_video_by_id(id, user_level)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"video": video}
    except Exception as e:
        print(f"Error fetching video {id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching video")
