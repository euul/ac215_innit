# 1. READING HTML
# load libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

# specify url to scrape
url = 'https://www.bbc.com/news'
headers = {
    "authority": "learnenglishteens.britishcouncil.org",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# alternative-1 (online parsing)
page = requests.get(url, headers=headers).text

# create an object to scrape various data later
soup = BeautifulSoup(page, 'html.parser')

print("HTML Parsed Successfully")

# 2. PARSING HTML
props = soup.find('script', id='__NEXT_DATA__').string
json_data = json.loads(props)

sections = json_data["props"]["pageProps"]["page"]["@\"news\","]["sections"]

# Initialize lists to store data for DataFrame
titles = []
hrefs = []
metadatas = []
texts = []

# Initialize a counter for tracking how many articles have been scraped
counter = 0

# Loop over sections to extract title, href, metadata, and text for each article
for section in sections:
    for content_item in section.get("content", []):
        title = content_item.get("title")
        href = content_item.get("href")
        metadata = content_item.get("metadata")

        # Add the data to the lists
        titles.append(title)
        hrefs.append(href)
        metadatas.append(metadata)

        # For each href, scrape the article's text
        if href:
            article_url = 'https://www.bbc.com' + href
            print(f"Scraping article: {article_url}")
            
            # Try-except block to handle connection errors
            try:
                article_page = requests.get(article_url, headers=headers, timeout=10).text
                article_soup = BeautifulSoup(article_page, 'html.parser')

                # Find all text-block divs in the article
                text_block_divs = article_soup.find_all('div', {'data-component': 'text-block'})
                
                # Initialize an empty string to accumulate the text
                all_text = ""
                for div in text_block_divs:
                    all_text += div.get_text(strip=True) + " "  # Concatenate text from each block
                
                texts.append(all_text)
            
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {article_url}: {e}")
                texts.append(None)  # Append None for articles that couldn't be scraped
            
            time.sleep(1)  # Sleep for 1 second to avoid overwhelming the server
        
        # Increment the counter
        counter += 1
        
        # Every 10 articles, save to CSV and reset the lists
        if counter % 10 == 0:
            print(f"Saving results after {counter} articles...")
            # Create a DataFrame from the lists
            data = {
                'Title': titles,
                'Href': hrefs,
                'Metadata': metadatas,
                'Text': texts
            }
            df = pd.DataFrame(data)
            df = df.dropna()
            df.to_csv('bbc_news_articles.csv', index=False, mode='a', header=True)  # Append to the CSV file
            # Clear the lists to prepare for the next batch of articles
            titles.clear()
            hrefs.clear()
            metadatas.clear()
            texts.clear()

# Final save after all articles are scraped
print("Saving final results...")
data = {
    'Title': titles,
    'Href': hrefs,
    'Metadata': metadatas,
    'Transcript': texts
}
df = pd.DataFrame(data)
df = df.dropna()
df.to_csv('bbc_news_articles.csv', index=False, mode='a', header=True)  # Append to the CSV file

print("Number of Results: ", len(titles))