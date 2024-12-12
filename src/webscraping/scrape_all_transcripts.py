import pandas as pd
import requests
from bs4 import BeautifulSoup
from google.cloud import storage
import json


# Define the GCP bucket
bucket_name = 'innit_articles_bucket'

# Function to read JSON data from GCP bucket and convert it to DataFrame
def read_json_from_gcp(bucket_name, blob_name):
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    # Get the blob (file)
    blob = bucket.blob(blob_name)
    # Download the blob content as a strings
    json_data = blob.download_as_text()
    # Convert the JSON string to a DataFrame
    return pd.read_json(json_data)

# Function to upload the scraped data to a GCP bucket in JSON format
def upload_to_gcp_bucket(bucket_name, blob_name, data):
    # Initialize the GCP client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(blob_name)

    # Convert the DataFrame to JSON and upload
    json_data = data.to_json(orient='records', lines=True)
    blob.upload_from_string(json_data, content_type='application/json')

    print(f"Data uploaded to GCP bucket {bucket_name} with blob name {blob_name}")


def scrape_transcripts(bucket_name, blob_name, target_blob_name):
    # Read all the links from the CSV file
    df = read_json_from_gcp(bucket_name, blob_name)

    # Initialize lists to store the scraped data
    transcripts = []
    levels = []
    topics = []
    links_processed = []
    missing_transcripts_urls = []


    if blob_name == "scraped_all_links.json":
        url_root = 'https://learnenglish.britishcouncil.org'
        # Headers to include in the request
        headers = {
            "authority": "learnenglish.britishcouncil.org",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
    elif blob_name == "scraped_all_links_teens.json":
        url_root = 'https://learnenglishteens.britishcouncil.org'
        # Headers to include in the request
        headers = {
            "authority": "learnenglishteens.britishcouncil.org",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        
    # Loop through each link in the CSV
    for index, row in df.iterrows():
        # Construct the full link
        link_complete = url_root + row['Link']
        print(f"Scraping {link_complete}...")

        # Make the request
        response = requests.get(link_complete, headers=headers)

        if response.status_code == 200:
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')


            # Transcript or Reading Text
            cases = [
                {"tag": "div", "class": "field field--name-field-tapescript field--type-text-long field--label-hidden field--item"},
                {"tag": "div", "class": "field field--name-field-reading-text field--type-text-long field--label-hidden field--item"},
                {"tag": "div", "class": "field field--name-field-transcript field--type-text-long field--label-hidden field--item"}
                ]
            
            for case in cases:
                tag = case.get("tag")
                class_name = case.get("class")
                transcript_div = soup.find(tag, class_=class_name)

                if transcript_div:
                    transcript = transcript_div.get_text(separator='\n')
                    break
            if not transcript:
                transcript = "Transcript/Reading text not found"
                # Add the URL to the missing list if neither is found
                missing_transcripts_urls.append(link_complete)

            # Label (Language Level)
            if blob_name == "scraped_all_links.json":
                level_div = soup.find('h3', string="Language level")
            elif blob_name == "scraped_all_links_teens.json": 
                level_div = soup.find('div', string="Language level")

            if level_div:
                level_div = level_div.find_next_sibling('div')
                level = level_div.find("div", class_="field--item").find("a").get_text() if level_div else "Level not found"
            else:
                level = "Level not found"
            

            # Topic (Handling multiple topics)
            if blob_name == "scraped_all_links.json":
                topic_div = soup.find('h3', string="Topics")
            elif blob_name == "scraped_all_links_teens.json": 
                topic_div = soup.find('div', string="Topics")

            if topic_div:
                topic_div = topic_div.find_next_sibling('div')
                topic_items = topic_div.find_all("div", class_="field--item")
                # Collect all topics and concatenate them
                topic = ', '.join([item.get_text() for item in topic_items]) if topic_items else "Topic not found"
            else:
                topic = "Topic not found"

            # Append the data to the lists
            transcripts.append(transcript)
            levels.append(level)
            topics.append(topic)
            links_processed.append(link_complete)

        else:
            print(f"Failed to retrieve {link_complete}. Status code: {response.status_code}")
            transcripts.append("Failed to retrieve")
            levels.append("Failed to retrieve")
            topics.append("Failed to retrieve")
            links_processed.append(link_complete)

    # Create a DataFrame with all the scraped data
    scraped_data = pd.DataFrame({
        'Link': links_processed,
        'Transcript': transcripts,
        'Label': levels,
        'Topic': topics
    })

    # Save the scraped data to a JSON file
    scraped_data.to_json(target_blob_name, orient='records', lines=True)

    # Upload the scraped content to the GCP bucket (add this if needed)
    upload_to_gcp_bucket(bucket_name, target_blob_name, scraped_data)


    # Save the URLs of pages missing transcript/reading text to a txt file
    with open('missing_transcripts.txt', 'w') as f:
        for url in missing_transcripts_urls:
            f.write(f"{url}\n")

    print(f"Missing transcripts or reading texts URLs have been saved to missing_transcripts.txt")

def main():  # pragma: no cover
    print("Scraping adult transcripts...")
    scrape_transcripts(bucket_name, 'scraped_all_links.json', 'scraped_all_content.json')

    print("Scraping teen transcripts...")
    scrape_transcripts(bucket_name, 'scraped_all_links_teens.json', 'scraped_all_content_teens.json')


if __name__ == "__main__":
    main()
