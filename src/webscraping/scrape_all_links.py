import requests
from bs4 import BeautifulSoup
import pandas as pd

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

    # Save the titles and links into a pandas DataFrame
    df = pd.DataFrame({'Title': all_titles, 'Link': all_links})

    # Save the DataFrame to a CSV file
    if teens == False:
        df.to_csv('scraped_all_links.csv', index=False)
        print("Scraping complete. All data saved to 'scraped_all_links.csv'.")
    else:
        df.to_csv('scraped_all_links_teens.csv', index=False)
        print("Scraping complete. All data saved to 'scraped_all_links_teens.csv'.")

    

scrape_links("target_links.txt",False)
scrape_links("target_links_teens.txt",True)
