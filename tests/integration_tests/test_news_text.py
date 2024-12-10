import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import requests
import json
import pandas as pd
import os
from bs4 import BeautifulSoup
import sys
# import torch
from datasets import Dataset

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from get_bbc_news import (
    fetch_page,
    parse_sections,
    scrape_article,
    save_to_csv,
    scrape_bbc_news,
)

from upload_articles import save_df_to_json, upload_json_to_gcp

# from level_articles import (
#     download_json_from_gcp,
#     convert_json_to_hf_dataset,
#     download_weights,
#     # load_model,
#     infer,
#     upload_predictions_to_gcp_json,
#     LABEL_MAPPING
# )

class TestBBCNewsScraper(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_page(self, mock_get):
        # Mock requests.get to return a fake HTML page
        mock_get.return_value.text = "<html><head><title>Test</title></head></html>"
        headers = {"user-agent": "test-agent"}
        soup = fetch_page("http://test.com", headers)

        # Assertions
        mock_get.assert_called_once_with("http://test.com", headers=headers)
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.title.string, "Test")

    def test_parse_sections(self):
        # Mock BeautifulSoup object with JSON-like script
        mock_soup = MagicMock()
        mock_soup.find.return_value.string = json.dumps({
            "props": {
                "pageProps": {
                    "page": {
                        "@\"news\",": {
                            "sections": [{"content": [{"title": "Sample Title"}]}]
                        }
                    }
                }
            }
        })

        sections = parse_sections(mock_soup)

        # Assertions
        mock_soup.find.assert_called_once_with('script', id='__NEXT_DATA__')
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["content"][0]["title"], "Sample Title")

    @patch("requests.get")
    def test_scrape_article(self, mock_get):
        # Mock requests.get to return a fake article page
        mock_get.return_value.text = """
            <html>
                <div data-component="text-block">Sample text 1</div>
                <div data-component="text-block">Sample text 2</div>
            </html>
        """
        headers = {"user-agent": "test-agent"}
        article_text = scrape_article("http://test-article.com", headers)

        # Assertions
        mock_get.assert_called_once_with("http://test-article.com", headers=headers, timeout=10)
        self.assertEqual(article_text, "Sample text 1 Sample text 2")

    @patch("pandas.DataFrame.to_csv")
    def test_save_to_csv(self, mock_to_csv):
        # Mock input data
        titles = ["Title 1", "Title 2"]
        hrefs = ["/article1", "/article2"]
        metadatas = ["Meta1", "Meta2"]
        texts = ["Text 1", "Text 2"]

        # Call the function
        save_to_csv(titles, hrefs, metadatas, texts, filepath='bbc_news/bbc_news_articles.csv')

        # Assertions
        mock_to_csv.assert_called_once()
        args, kwargs = mock_to_csv.call_args

        # Verify the filename passed as the first positional argument
        self.assertEqual(args[0], "bbc_news/bbc_news_articles.csv")

        # Verify additional keyword arguments
        self.assertEqual(kwargs.get("index", False), False)  # Check if 'index' is False
        self.assertEqual(kwargs.get("mode", "w"), "a")  # Check if 'mode' is 'a'


    @patch("get_bbc_news.scrape_article")
    @patch("get_bbc_news.save_to_csv")
    @patch("get_bbc_news.fetch_page")
    @patch("get_bbc_news.parse_sections")
    def test_scrape_bbc_news(self, mock_parse_sections, mock_fetch_page, mock_save_to_csv, mock_scrape_article):
        # Mock BeautifulSoup page and sections
        mock_soup = MagicMock()
        mock_fetch_page.return_value = mock_soup
        mock_parse_sections.return_value = [
            {
                "content": [
                    {"title": "Article 1", "href": "/article1", "metadata": "Meta1"},
                    {"title": "Article 2", "href": "/article2", "metadata": "Meta2"},
                ]
            }
        ]
        mock_scrape_article.side_effect = ["Text 1", "Text 2"]

        headers = {"user-agent": "test-agent"}
        scrape_bbc_news("http://test.com", headers)

        # Assertions
        mock_fetch_page.assert_called_once_with("http://test.com", headers)
        mock_parse_sections.assert_called_once_with(mock_soup)
        self.assertEqual(mock_scrape_article.call_count, 2)
        mock_save_to_csv.assert_called()


# class TestLevelArticles(unittest.TestCase):

#     @patch("level_articles.storage.Client")
#     def test_download_json_from_gcp(self, mock_storage_client):
#         mock_blob = MagicMock()
#         mock_bucket = MagicMock()
#         mock_bucket.blob.return_value = mock_blob
#         mock_storage_client.return_value.bucket.return_value = mock_bucket

#         # Call the function
#         download_json_from_gcp("test_bucket", "test_blob.json", "local_file.json")

#         # Assertions
#         mock_storage_client.assert_called_once()
#         mock_bucket.blob.assert_called_once_with("test_blob.json")
#         mock_blob.download_to_filename.assert_called_once_with("local_file.json")

#     @patch("builtins.open", new_callable=mock_open, read_data='{"Text": "Sample text"}\n{"Text": "Another sample"}')
#     @patch("level_articles.Dataset.from_list")
#     def test_convert_json_to_hf_dataset(self, mock_from_list, mock_file):
#         dataset = MagicMock()
#         mock_from_list.return_value = dataset

#         result = convert_json_to_hf_dataset("local_file.json")

#         # Assertions
#         mock_file.assert_called_once_with("local_file.json", "r")
#         mock_from_list.assert_called_once()
#         self.assertEqual(result, dataset)

#     @patch("level_articles.storage.Client")
#     def test_download_weights(self, mock_storage_client):
#         # Case: file already exists
#         with patch("os.path.exists", return_value=True):
#             download_weights("test_bucket", "test_blob.pth", "local_weights.pth")
#             mock_storage_client.assert_not_called()

#         # Case: file does not exist
#         with patch("os.path.exists", return_value=False):
#             mock_blob = MagicMock()
#             mock_bucket = MagicMock()
#             mock_bucket.blob.return_value = mock_blob
#             mock_storage_client.return_value.bucket.return_value = mock_bucket

#             download_weights("test_bucket", "test_blob.pth", "local_weights.pth")

#             mock_storage_client.assert_called_once()
#             mock_bucket.blob.assert_called_once_with("test_blob.pth")
#             mock_blob.download_to_filename.assert_called_once_with("local_weights.pth")

#     # @patch("level_articles.AutoModelForSequenceClassification.from_pretrained")
#     # @patch("torch.load")
#     # def test_load_model(self, mock_torch_load, mock_from_pretrained):
#     #     mock_model = MagicMock()
#     #     mock_from_pretrained.return_value = mock_model

#     #     model = load_model("weights.pth", 5)

#     #     # Assertions
#     #     mock_from_pretrained.assert_called_once_with("microsoft/deberta-v3-small", num_labels=5)
#     #     mock_torch_load.assert_called_once_with("weights.pth", map_location=torch.device("cpu"))
#     #     mock_model.load_state_dict.assert_called_once_with(mock_torch_load.return_value)
#     #     mock_model.eval.assert_called_once()
#     #     self.assertEqual(model, mock_model)

#     @patch("level_articles.storage.Client")
#     @patch("pandas.DataFrame.to_json")
#     @patch("os.remove")
#     def test_upload_predictions_to_gcp_json(self, mock_remove, mock_to_json, mock_storage_client):
#         # Create a Hugging Face Dataset
#         dataset = Dataset.from_dict({"Text": ["Sample"], "predictions": ["A1"]})

#         # Mock GCP bucket and blob behavior
#         mock_blob = MagicMock()
#         mock_bucket = MagicMock()
#         mock_bucket.blob.return_value = mock_blob
#         mock_storage_client.return_value.bucket.return_value = mock_bucket

#         # Call the refactored function
#         upload_predictions_to_gcp_json(dataset, "test_bucket", "labeled.json")

#         # Assertions
#         mock_to_json.assert_called_once_with("temp_predictions.json", orient="records", lines=True)  # Check file write
#         mock_blob.upload_from_filename.assert_called_once_with("temp_predictions.json")  # Verify upload
#         mock_remove.assert_called_once_with("temp_predictions.json")  # Ensure temp file is deleted


class TestUploadArticles(unittest.TestCase):

    @patch("upload_articles.os.makedirs")
    @patch("upload_articles.pd.DataFrame.to_json")
    def test_save_df_to_json(self, mock_to_json, mock_makedirs):
        """Test saving a DataFrame to a JSON file."""
        df = pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})
        json_file_path = "output/test.json"

        # Call the function
        save_df_to_json(df, json_file_path)

        # Assert that directories are created and DataFrame is saved as JSON
        mock_makedirs.assert_called_once_with(os.path.dirname(json_file_path), exist_ok=True)
        mock_to_json.assert_called_once_with(json_file_path, orient='records', lines=True)

    @patch("upload_articles.storage.Client")
    def test_upload_json_to_gcp(self, mock_storage_client):
        """Test uploading a JSON file to a GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test_bucket"
        destination_blob_name = "path/to/destination.json"
        json_file_path = "output/test.json"

        # Call the function
        upload_json_to_gcp(bucket_name, destination_blob_name, json_file_path)

        # Assert GCP client interactions
        mock_storage_client.return_value.bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(destination_blob_name)
        mock_blob.upload_from_filename.assert_called_once_with(json_file_path)

    @patch("upload_articles.upload_json_to_gcp")
    @patch("upload_articles.save_df_to_json")
    @patch("pandas.read_csv")
    def test_main(self, mock_read_csv, mock_save_df_to_json, mock_upload_json_to_gcp):
        """Test the main function."""
        # Mock DataFrame
        df_mock = MagicMock()
        df_mock.dropna.return_value = df_mock
        mock_read_csv.return_value = df_mock

        # Call the main function
        with patch("upload_articles.__name__", "__main__"):
            import upload_articles
            upload_articles.main()

        # Assert DataFrame is read and null values are removed
        mock_read_csv.assert_called_once_with('bbc_news/bbc_news_articles.csv')
        df_mock.dropna.assert_called_once()

        # Assert save and upload functions are called
        mock_save_df_to_json.assert_called_once_with(df_mock, "bbc_news/bbc_news_articles.json")
        mock_upload_json_to_gcp.assert_called_once_with(
            'innit_articles_bucket', 
            "bbc_news/bbc_news_articles.json", 
            "bbc_news/bbc_news_articles.json"
        )



if __name__ == "__main__":
    unittest.main()
