import pandas as pd
import requests
from bs4 import BeautifulSoup

# Read all the links from the CSV file
df = pd.read_csv('scraped_all_links.csv')

# Initialize lists to store the scraped data
transcripts = []
levels = []
topics = []
links_processed = []
missing_transcripts_urls = []

# Loop through each link in the CSV
for index, row in df.iterrows():
    # Construct the full link
    link_complete = 'https://learnenglish.britishcouncil.org' + row['Link']
    print(f"Scraping {link_complete}...")

    # Headers to include in the request
    headers = {
        "authority": "learnenglish.britishcouncil.org",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    # Make the request
    response = requests.get(link_complete, headers=headers)

    if response.status_code == 200:
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Transcript or Reading Text
        transcript_div = soup.find("div", class_="field field--name-field-tapescript field--type-text-long field--label-hidden field--item")
        if not transcript_div:
            # Check for 'Reading text' if 'Transcript' is not found
            transcript_div = soup.find("div", class_="field field--name-field-reading-text field--type-text-long field--label-hidden field--item")
        
        if transcript_div:
            transcript = transcript_div.get_text(separator='\n')
        else:
            transcript = "Transcript/Reading text not found"
            # Add the URL to the missing list if neither is found
            missing_transcripts_urls.append(link_complete)

        # Label (Language Level)
        level_div = soup.find('h3', string="Language level")
        if level_div:
            level_div = level_div.find_next_sibling('div')
            level = level_div.find("div", class_="field--item").find("a").get_text() if level_div else "Level not found"
        else:
            level = "Level not found"

        # Topic (Handling multiple topics)
        topic_div = soup.find('h3', string="Topics")
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

# Save the DataFrame to a CSV file
scraped_data.to_csv('scraped_all_content.csv', index=False)
print(f"All data has been written to scraped_all_content.csv")

# Save the URLs of pages missing transcript/reading text to a txt file
with open('missing_transcripts.txt', 'w') as f:
    for url in missing_transcripts_urls:
        f.write(f"{url}\n")

print(f"Missing transcripts or reading texts URLs have been saved to missing_transcripts.txt")

