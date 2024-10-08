import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape titles and links from a given URL
def scrape_page(url):
    full_url = "https://learnenglish.britishcouncil.org/" + url

    # Headers to include in the request
    headers = {
        "authority": "learnenglish.britishcouncil.org",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    # Make the GET request
    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all elements with the specific class
        title_elements = soup.find_all('div', class_='field field--name-node-title field--type-ds field--label-hidden field--item')

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

# Read URLs from a text file (each URL on a new line)
with open('target_links.txt', 'r') as f:  # Replace with the actual name of your text file
    urls = [line.strip() for line in f.readlines()]

# Initialize lists to store all the scraped data
all_titles = []
all_links = []

# Loop through each URL in the text file and scrape the titles/links
for url in urls:
    print(f"Scraping: {url}")
    titles, links = scrape_page(url)
    
    # Append the scraped titles and links to the main lists
    all_titles.extend(titles)
    all_links.extend(links)

# Save the titles and links into a pandas DataFrame
df = pd.DataFrame({'Title': all_titles, 'Link': all_links})

# Save the DataFrame to a CSV file
df.to_csv('scraped_all_links.csv', index=False)

print("Scraping complete. All data saved to 'scraped_listening_links.csv'.")
