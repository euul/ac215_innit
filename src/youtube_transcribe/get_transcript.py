from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from google.cloud import storage

def get_yt_video_id(url):
    parsed_url = urlparse(url)

    # Case 1: URL contains 'v' parameter in query (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v")
        if video_id:
            return video_id[0]
    
    # Case 2: URL is a shortened youtu.be link (e.g., https://youtu.be/VIDEO_ID)
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    
    # Case 3: Embedded video URL (e.g., https://www.youtube.com/embed/VIDEO_ID)
    elif parsed_url.path.startswith("/embed/"):
        return parsed_url.path.split("/")[2]
    
    # If no ID was found
    else:
        return None

def get_transcript(url):
    video_id = get_yt_video_id(url)
    print(video_id)
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
    
def save_transcript(transcript, title = 'output.txt'):
    filename = title
    with open(filename, "w") as file:
        for entry in transcript:
            file.write(f"{entry['start']}: {entry['text']}\n")
    print(f"Transcript saved to {filename}")

def upload_to_gcp_bucket(bucket_name, folder_name, blob_name, text_file_path):
    # Initialize the GCP client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    blob_path = f"{folder_name}/{blob_name}"
    blob = bucket.blob(blob_path)

    # Read the .txt file and upload
    with open(text_file_path, "r") as file:
        text_data = file.read()

    blob.upload_from_string(text_data, content_type='text/plain')
    print(f"Text file uploaded to GCP bucket '{bucket_name}' in folder '{folder_name}' with blob name '{blob_name}'")



youtube_url = "https://www.youtube.com/watch?v=Lx4poQw1mZo"
transcript = get_transcript(youtube_url)

if transcript:
    transcript_filename = "output.txt"
    save_transcript(transcript, transcript_filename)

    # # Upload to GCP as a .txt file
    # bucket_name = 'innit_articles_bucket'
    # folder_name = 'yt_transcripts'
    # upload_to_gcp_bucket(bucket_name, folder_name, transcript_filename, transcript_filename)
