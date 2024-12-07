import json
import traceback
from typing import List, Dict, Optional
from google.cloud import storage

class MediaManager:
    def __init__(self, bucket_name: str):
        """Initialize the MediaManager with the GCP bucket name."""
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

    def _fetch_json_files_from_gcp(self, folder_prefix: str) -> List[Dict]:
        """Fetch and parse JSON files from a specific folder in the GCP bucket."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blobs = bucket.list_blobs(prefix=folder_prefix)

            data = []
            for blob in blobs:
                if blob.name.endswith(".json"):  # Process only JSON files
                    content = blob.download_as_text()
                    parsed_content = json.loads(content)
                    data.append(parsed_content)
            return data
        except Exception as e:
            print(f"Error fetching data from GCP: {str(e)}")
            traceback.print_exc()
            return []

    def get_video_transcripts(self, folder_prefix: str = "yt_transcripts/B2/") -> List[Dict]:
        """Fetch video transcripts from the specified folder in the GCP bucket."""
        return self._fetch_json_files_from_gcp(folder_prefix)

    def get_articles(self, folder_prefix: str = "bbc_news/B2/") -> List[Dict]:
        """Fetch articles from the specified folder in the GCP bucket."""
        return self._fetch_json_files_from_gcp(folder_prefix)

    def get_article_by_id(self, article_id: str, folder_prefix: str = "bbc_news/B2/") -> Optional[Dict]:
        """Fetch a single article by ID."""
        try:
            articles = self.get_articles(folder_prefix)  # Fetch all articles
            return next((article for article in articles if str(article.get("id")) == article_id), None)
        except Exception as e:
            print(f"Error fetching article with ID {article_id}: {str(e)}")
            traceback.print_exc()
            return None
        
    def get_video_by_id(self, video_id: str, folder_prefix: str = "yt_transcripts/B2/") -> Optional[Dict]:
        """Fetch a single video by ID."""
        try:
            videos = self.get_video_transcripts(folder_prefix)  # Fetch all videos
            return next((video for video in videos if str(video.get("video_id")) == video_id), None)
        except Exception as e:
            print(f"Error fetching video with ID {video_id}: {str(e)}")
            traceback.print_exc()
            return None
