from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import storage
import json
import shutil
import os
import video_id_scraper
import argparse

parser = argparse.ArgumentParser(description="Scrape YouTube search results.")
parser.add_argument("--keyword", type=str, help="Search keyword for YouTube.")
parser.add_argument("--n_scroll", type=int, default=2, help="Number of scroll actions to load content (default: 2)")
args = parser.parse_args()

def get_transcript(video_id):
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            for entry in transcript:
                entry['start'] = clean_timestamps(entry['start'])
            return transcript
        except Exception as e:
            print(f"Error retrieving transcript: {e}")
            return None
    else:
        print("Invalid YouTube URL or video ID not found.")
        return None

def clean_timestamps(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"
    

def upload_to_gcp_bucket(bucket_name, folder_name, local_folder):
    # Initialize the GCP client
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    # Upload each JSON file in the local folder
    for filename in os.listdir(local_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(local_folder, filename)
            blob_path = f"{folder_name}/{filename}"
            blob = bucket.blob(blob_path)

            # Upload JSON file to GCP bucket
            blob.upload_from_filename(file_path, content_type='application/json')
            print(f"Uploaded '{filename}' to GCP bucket '{bucket_name}' in folder '{folder_name}'")

def save_transcripts(videos, local_folder):
    # Ensure the local folder exists
    os.makedirs(local_folder, exist_ok=True)

    # Save each transcript as a JSON file in the local folder
    for video in videos:
        transcript = get_transcript(video["video_id"])
        if transcript:
            data = {
                "video_name": video["video_name"],
                "video_id": video["video_id"],
                "transcript": transcript
            }
            transcript_filename = f"{video['video_name']}.json"
            file_path = os.path.join(local_folder, transcript_filename)

            # Save data to a JSON file
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Saved transcript for '{video['video_name']}' locally.")

# videos = [
#     {"video_name": "ai_and_math", "video_id": "e049IoFBnLA"},
#     {"video_name": "john_oliver_trump_reelection", "video_id": "LU2atCWyAos"},
#     # Add more video dictionaries as needed
# ]

videos = video_id_scraper.main(args.keyword, args.n_scroll)

def cleanup_local_folder(local_folder):
    shutil.rmtree(local_folder)
    print(f"Deleted local folder '{local_folder}' and all its contents.")

local_folder = "transcripts"
bucket_name = 'innit_articles_bucket'
folder_name = 'yt_transcripts'

# Save all transcripts locally
save_transcripts(videos, local_folder)

# Upload all saved JSON files to the GCP bucket in a single batch
upload_to_gcp_bucket(bucket_name, folder_name, local_folder)

# Clean up the local transcripts folder
cleanup_local_folder(local_folder)


