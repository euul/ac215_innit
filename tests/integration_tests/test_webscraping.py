import os
import sys
import gc
import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import pandas as pd

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from scrape_all_links import scrape_page, upload_to_gcp_bucket as upload_links_to_gcp, scrape_links
from scrape_all_transcripts import read_json_from_gcp, upload_to_gcp_bucket as upload_transcripts_to_gcp, scrape_transcripts


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
    def test_upload_to_gcp_bucket_webscrape(self, mock_storage_client):
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
        upload_links_to_gcp(bucket_name, blob_name, data)

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
            temp_file.write("skills/listening/a1-listening\nskills/listening/a2-listening\n")
            temp_file_name = temp_file.name

        try:
            # Mock scrape_page responses
            mock_scrape_page.side_effect = [
                (["Title 1"], ["/link1"]),
                (["Title 2"], ["/link2"]),
            ]

            # Test scrape_links
            scrape_links(temp_file_name, False)

            # Assertions
            mock_scrape_page.assert_any_call("skills/listening/a1-listening", False)
            mock_scrape_page.assert_any_call("skills/listening/a2-listening", False)
            mock_upload_to_gcp.assert_called_once_with(
                "innit_articles_bucket",
                "scraped_all_links.json",
                {"Title": ["Title 1", "Title 2"], "Link": ["/link1", "/link2"]},
            )

        finally:
            # Clean up: Delete the temporary file
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)

    @patch("scrape_all_transcripts.storage.Client")
    def test_read_json_from_gcp(self, mock_storage_client):
        # Mock the GCP client and its return values
        mock_blob = MagicMock()
        mock_blob.download_as_text.return_value = '{"Link": ["/link1", "/link2"]}'
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        # Test the function
        df = read_json_from_gcp("test_bucket", "test_blob.json")

        # Assertions
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("Link", df.columns)
        self.assertEqual(df.loc[0, "Link"], "/link1")

    @patch("scrape_all_transcripts.requests.get")
    @patch("scrape_all_transcripts.upload_to_gcp_bucket")
    @patch("scrape_all_transcripts.read_json_from_gcp")
    def test_scrape_transcripts(self, mock_read_json, mock_upload_to_gcp, mock_requests_get):
        # Mock the read_json_from_gcp function
        mock_read_json.return_value = pd.DataFrame({"Link": ["/link1", "/link2"]})

        # Mock requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
            <div class='field field--name-field-transcript field--type-text-long field--label-hidden field--item'>
                Sample transcript
            </div>
        """
        mock_requests_get.return_value = mock_response

        # Test scrape_transcripts
        scrape_transcripts("test_bucket", "test_blob.json", "output_blob.json")

        # Assertions
        mock_read_json.assert_called_once_with("test_bucket", "test_blob.json")
        mock_requests_get.assert_called_once()
        mock_upload_to_gcp.assert_called_once()

    def tearDown(self):
        gc.collect()


if __name__ == "__main__":
    unittest.main()
