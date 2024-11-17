import os
import sys
import unittest
from unittest.mock import patch, Mock
import tempfile

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from scrape_all_links import scrape_page, upload_to_gcp_bucket, scrape_links

class TestWebScraping(unittest.TestCase):

    @patch("scrape_all_links.requests.get")
    def test_scrape_page_success(self, mock_get):
        # Mock the requests.get() response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
            <div class='field field--name-node-title field--type-ds field--label-hidden field--item'>
                <a href="/path/to/resource">Test Title</a>
            </div>
        """
        mock_get.return_value = mock_response

        # Test the function
        titles, links = scrape_page("example-url", False)

        # Assertions
        self.assertEqual(titles, ["Test Title"])
        self.assertEqual(links, ["/path/to/resource"])

    @patch("scrape_all_links.requests.get")
    def test_scrape_page_failure(self, mock_get):
        # Mock a failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test the function
        titles, links = scrape_page("example-url", False)

        # Assertions
        self.assertEqual(titles, [])
        self.assertEqual(links, [])

    @patch("scrape_all_links.storage.Client")
    def test_upload_to_gcp_bucket(self, mock_storage_client):
        # Mock the GCP client
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Test data
        bucket_name = "test_bucket"
        blob_name = "test_blob.json"
        data = {"Title": ["Test Title"], "Link": ["https://example.com"]}

        # Test the function
        upload_to_gcp_bucket(bucket_name, blob_name, data)

        # Assertions
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with(blob_name)
        mock_blob.upload_from_string.assert_called_once_with(
            '{"Title": ["Test Title"], "Link": ["https://example.com"]}', content_type="application/json"
        )

    @patch("scrape_all_links.scrape_page")
    @patch("scrape_all_links.upload_to_gcp_bucket")
    def test_scrape_links(self, mock_upload_to_gcp, mock_scrape_page):
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("skills/listening/a1-listening\nskills/listening/a2-listening\nskills/listening/b1-listening\nskills/listening/b2-listening")
            temp_file_name = temp_file.name
        
        try:
            # Mock scrape_page responses
            mock_scrape_page.side_effect = [
                (["Title 1"], ["/link1"]),
                (["Title 2"], ["/link2"]),
                (["Title 3"], ["/link3"]),
                (["Title 4"], ["/link4"]),
            ]

            # Test the function with the temporary file
            scrape_links(temp_file_name, False)

            # Assertions
            mock_scrape_page.assert_any_call("skills/listening/a1-listening", False)
            mock_scrape_page.assert_any_call("skills/listening/a2-listening", False)
            mock_scrape_page.assert_any_call("skills/listening/b1-listening", False)
            mock_scrape_page.assert_any_call("skills/listening/b2-listening", False)
            mock_upload_to_gcp.assert_called_once_with(
                "innit_articles_bucket",
                "scraped_all_links.json",
                {"Title": ["Title 1", "Title 2", "Title 3", "Title 4"], "Link": ["/link1", "/link2", "/link3", "/link4"]},
            )
        
        finally:
            # Clean up: Delete the temporary file
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)

if __name__ == "__main__":
    unittest.main()
