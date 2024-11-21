from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time


def fetch_page(url, headers):
    """Fetch the HTML content of the given URL."""
    try:
        page = requests.get(url, headers=headers).text
        print("HTML Parsed Successfully")
        return BeautifulSoup(page, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


def parse_sections(soup):
    """Parse sections from the BeautifulSoup object."""
    try:
        props = soup.find('script', id='__NEXT_DATA__').string
        json_data = json.loads(props)
        return json_data["props"]["pageProps"]["page"]["@\"news\","]["sections"]
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error parsing sections: {e}")
        return []


def scrape_article(article_url, headers):
    """Scrape the text content of an article."""
    try:
        article_page = requests.get(article_url, headers=headers, timeout=10).text
        article_soup = BeautifulSoup(article_page, 'html.parser')
        text_block_divs = article_soup.find_all('div', {'data-component': 'text-block'})
        return " ".join(div.get_text(strip=True) for div in text_block_divs)
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {article_url}: {e}")
        return None


def save_to_csv(titles, hrefs, metadatas, texts, filename='bbc_news_articles.csv'):
    """Save scraped data to a CSV file."""
    data = {
        'Title': titles,
        'Href': hrefs,
        'Metadata': metadatas,
        'Text': texts
    }
    df = pd.DataFrame(data).dropna()
    df.to_csv(filename, index=False, mode='a', header=not pd.io.common.file_exists(filename))
    print(f"Saved {len(titles)} articles to {filename}")


def scrape_bbc_news(url, headers):
    """Main scraping function for BBC news articles."""
    soup = fetch_page(url, headers)
    if not soup:
        return

    sections = parse_sections(soup)
    if not sections:
        return

    titles, hrefs, metadatas, texts = [], [], [], []
    counter = 0

    for section in sections:
        for content_item in section.get("content", []):
            title = content_item.get("title")
            href = content_item.get("href")
            metadata = content_item.get("metadata")

            titles.append(title)
            hrefs.append(href)
            metadatas.append(metadata)

            if href:
                article_url = 'https://www.bbc.com' + href
                print(f"Scraping article: {article_url}")
                texts.append(scrape_article(article_url, headers))
                time.sleep(1)

            counter += 1
            if counter % 10 == 0:
                save_to_csv(titles, hrefs, metadatas, texts)
                titles.clear()
                hrefs.clear()
                metadatas.clear()
                texts.clear()

    # Final save after all articles are scraped
    save_to_csv(titles, hrefs, metadatas, texts)
    print(f"Scraped {counter} articles in total.")


def main(): # pragma: no cover
    url = 'https://www.bbc.com/news'
    headers = {
        "authority": "learnenglishteens.britishcouncil.org",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    scrape_bbc_news(url, headers)


if __name__ == "__main__":
    main() # pragma: no cover
