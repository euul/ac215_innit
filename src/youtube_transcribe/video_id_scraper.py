import argparse
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_video_info(div):
    """Helper function to extract video title and ID from a given div."""
    title_element = div.find("a", id="video-title")
    
    if not title_element:
        return None  # Return None if title element is not found
    
    title = title_element.get("title", "").strip()
    href = title_element.get("href", "")
    
    if not title or not href or "=" not in href:
        return None
    
    href = href.split('=')[1]
    return {"video_name": title, "video_id": href}

def main(keyword, n_scroll=2):
    """Main function to scrape YouTube video information."""
    # Set up the Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")  # Disable sandboxing (necessary for Docker)
    options.add_argument("--disable-dev-shm-usage")  # Fixes resource-related issues in Docker
    options.add_argument("--remote-debugging-port=9222")  # Avoid 'DevToolsActivePort' error
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration

    print("Initializing Chrome WebDriver...")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("Driver initialized successfully.")

    # Visit the YouTube search page
    driver.set_page_load_timeout(180)  # Set a 3-minute timeout for page load
    url = f"https://www.youtube.com/results?search_query={keyword}"
    # url = "https://www.stellardnn.org"
    driver.get(url)

    # Allow the page to load initial content
    time.sleep(2)

    print("Page loaded successfully.")

    # Scroll down in a loop to load more content
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    for _ in range(n_scroll):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            print("Reached the end of the page or no more content to load.")
            break
        last_height = new_height

    # Get the updated page source (HTML) after scrolling
    html = driver.page_source

    # Close the driver
    driver.quit()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all divs with id="title-wrapper"
    content_divs = soup.find_all("div", {"id": "title-wrapper"})
    
    # Collect video info from each div and return as a list of dictionaries
    results = [get_video_info(div) for div in content_divs]
    results = [result for result in results if result]  # Filter out None values

    return results

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Scrape YouTube search results.")
    parser.add_argument("--keyword", type=str, help="Search keyword for YouTube.")
    parser.add_argument("--n_scroll", type=int, default=2, help="Number of scroll actions to load content (default: 2)")

    args = parser.parse_args()
    video_results = main(args.keyword, args.n_scroll)
    