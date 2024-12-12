import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from google.cloud import storage

# Function to scrape titles and links from a given URL
def scrape_page(url, teens):
    if teens == False:
        full_url = "https://learnenglish.britishcouncil.org/" + url
        headers = {
        "authority": "learnenglish.britishcouncil.org",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    else:
        full_url = "https://learnenglishteens.britishcouncil.org/" + url
        headers = {
        "authority": "learnenglishteens.britishcouncil.org",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }


    # Make the GET request
    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all elements with the specific class
        if teens == False: 
            title_elements = soup.find_all('div', class_='field field--name-node-title field--type-ds field--label-hidden field--item')
        else: 
            title_elements = soup.find_all('div', class_='content-landing-list-content')

        # Extract title and link for each element
        titles = []
        links = []
        for element in title_elements:
            a_tag = element.find('a')
            if a_tag:
                titles.append(a_tag.text.strip())
                links.append(a_tag['href'])

        return titles, links
    else:
        print(f"Failed to retrieve the page: {url}. Status code: {response.status_code}")
        return [], []  # Return empty lists if the request fails


# Function to upload JSON data to a GCP bucket
def upload_to_gcp_bucket(bucket_name, blob_name, data):
    # Initialize the GCP client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(blob_name)

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Upload the JSON data to GCP
    blob.upload_from_string(json_data, content_type='application/json')

    print(f"Data uploaded to GCP bucket {bucket_name} with blob name {blob_name}")

def scrape_links(target_links,teens):
    # Read URLs from a text file (each URL on a new line)
    with open(target_links, 'r') as f:  # Replace with the actual name of your text file
        urls = [line.strip() for line in f.readlines()]

    # Initialize lists to store all the scraped data
    all_titles = []
    all_links = []

    # Loop through each URL in the text file and scrape the titles/links
    for url in urls:
        print(f"Scraping: {url}")
        titles, links = scrape_page(url, teens)
        
        # Append the scraped titles and links to the main lists
        all_titles.extend(titles)
        all_links.extend(links)

    # Create a dictionary of the scraped data
    scraped_data = {'Title': all_titles, 'Link': all_links}

    # Save the DataFrame to GCP
    bucket_name = 'innit_articles_bucket'
    if teens == False:
        blob_name = 'scraped_all_links.json'
    else:
        blob_name = 'scraped_all_links_teens.json'
    upload_to_gcp_bucket(bucket_name, blob_name, scraped_data)
    print(f"Scraping complete. All data saved to {blob_name}")


# Main function
def main():  # pragma: no cover
    # Define the files containing the URLs
    target_links_adults = "target_links.txt"
    target_links_teens = "target_links_teens.txt"

    # Scrape adult links
    print("Starting scrape for adult links...")
    scrape_links(target_links_adults, False)

    # Scrape teen links
    print("Starting scrape for teen links...")
    scrape_links(target_links_teens, True)


if __name__ == "__main__":
    main()
