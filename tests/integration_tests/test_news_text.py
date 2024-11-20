import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import requests
import json
import pandas as pd
import os
from bs4 import BeautifulSoup
import sys
import torch
from datasets import Dataset

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

import level_articles
import cli


class TestLevelArticles(unittest.TestCase):

    @patch("level_articles.storage.Client")
    def test_download_json_from_gcp(self, mock_storage_client):
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        # Call the function
        level_articles.download_json_from_gcp("test_bucket", "test_blob.json", "local_file.json")

        # Assertions
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_blob.json")
        mock_blob.download_to_filename.assert_called_once_with("local_file.json")

    @patch("level_articles.Dataset.from_list")
    @patch("builtins.open", new_callable=mock_open, read_data='{"Text": "Sample text"}\n{"Text": "Another sample"}')
    def test_convert_json_to_hf_dataset(self, mock_file, mock_from_list):
        dataset = MagicMock()
        mock_from_list.return_value = dataset

        result = level_articles.convert_json_to_hf_dataset("local_file.json")

        mock_file.assert_called_once_with("local_file.json", "r")
        mock_from_list.assert_called_once()
        self.assertEqual(result, dataset)

    @patch("level_articles.storage.Client")
    def test_download_weights(self, mock_storage_client):
        # Case: file already exists
        with patch("os.path.exists", return_value=True):
            level_articles.download_weights("test_bucket", "test_blob.pth", "local_weights.pth")
            mock_storage_client.assert_not_called()

        # Case: file does not exist
        with patch("os.path.exists", return_value=False):
            mock_blob = MagicMock()
            mock_bucket = MagicMock()
            mock_bucket.blob.return_value = mock_blob
            mock_storage_client.return_value.bucket.return_value = mock_bucket

            level_articles.download_weights("test_bucket", "test_blob.pth", "local_weights.pth")

            mock_storage_client.assert_called_once()
            mock_bucket.blob.assert_called_once_with("test_blob.pth")
            mock_blob.download_to_filename.assert_called_once_with("local_weights.pth")

    @patch("level_articles.AutoModelForSequenceClassification.from_pretrained")
    @patch("torch.load")
    def test_load_model(self, mock_torch_load, mock_from_pretrained):
        mock_model = MagicMock()
        mock_from_pretrained.return_value = mock_model

        model = level_articles.load_model("weights.pth", 5)

        mock_from_pretrained.assert_called_once_with("microsoft/deberta-v3-small", num_labels=5)
        mock_torch_load.assert_called_once_with("weights.pth", map_location=torch.device("cpu"))
        mock_model.load_state_dict.assert_called_once_with(mock_torch_load.return_value)
        mock_model.eval.assert_called_once()
        self.assertEqual(model, mock_model)

    # @patch("level_articles.AutoTokenizer.from_pretrained")
    # @patch("datasets.Dataset.map")  # Mock Hugging Face Dataset.map
    # @patch("torch.no_grad")
    # @patch("torch.argmax")
    # def test_infer(self, mock_argmax, mock_no_grad, mock_map, mock_tokenizer_from_pretrained):
    #     mock_model = MagicMock()

    #     # Create a Hugging Face Dataset
    #     mock_dataset = Dataset.from_dict({"Text": ["Sample text"]})

    #     # Simulate the output of Dataset.map (tokenized data)
    #     tokenized_dataset = Dataset.from_dict({
    #         "input_ids": [[101, 102]],
    #         "attention_mask": [[1, 1]]
    #     })
    #     mock_map.return_value = tokenized_dataset

    #     # Mock tokenizer behavior
    #     mock_tokenizer = MagicMock()
    #     mock_tokenizer_from_pretrained.return_value = mock_tokenizer

    #     # Mock predictions to return a PyTorch Tensor
    #     mock_predictions = torch.tensor([2])
    #     mock_argmax.return_value = mock_predictions
    #     mock_no_grad.return_value = MagicMock()

    #     # Call the function
    #     result_dataset = level_articles.infer(mock_model, mock_dataset)

    #     # Assertions
    #     mock_tokenizer_from_pretrained.assert_called_once_with("microsoft/deberta-v3-small")
    #     mock_map.assert_called_once_with(  # Verify map was called with the correct arguments
    #         lambda examples: mock_tokenizer(examples["Text"], truncation=True, padding="max_length", max_length=800),
    #         batched=True
    #     )
    #     mock_argmax.assert_called_once()  # Ensure torch.argmax was called
    #     self.assertTrue("predictions" in result_dataset.column_names)
    #     self.assertEqual(result_dataset["predictions"], ["B1"])  # Assuming LABEL_MAPPING[2] is "B1"



    # @patch("level_articles.storage.Client")
    # @patch("datasets.Dataset.to_pandas")  # Mock Dataset.to_pandas if used internally
    # @patch("pandas.DataFrame.to_json")
    # def test_upload_predictions_to_gcp_json(self, mock_to_json, mock_to_pandas, mock_storage_client):
    #     # Mock Hugging Face Dataset
    #     dataset = Dataset.from_dict({"Text": ["Sample"], "predictions": ["A1"]})
    #     mock_to_pandas.return_value = pd.DataFrame({"Text": ["Sample"], "predictions": ["A1"]})

    #     # Mock GCP bucket and blob behavior
    #     mock_blob = MagicMock()
    #     mock_bucket = MagicMock()
    #     mock_bucket.blob.return_value = mock_blob
    #     mock_storage_client.return_value.bucket.return_value = mock_bucket

    #     # Call the function
    #     level_articles.upload_predictions_to_gcp_json(dataset, "test_bucket", "labeled.json")

    #     # Assertions
    #     mock_storage_client.assert_called_once()  # Check the storage client was created
    #     mock_bucket.blob.assert_called_once_with("labeled.json")  # Verify blob() was called
    #     mock_blob.open.assert_called_once_with("w")  # Verify open() was called for writing
    #     mock_to_json.assert_called_once()  # Ensure DataFrame was converted to JSON



class TestGetBBCNews(unittest.TestCase):

    @patch("requests.get")
    @patch("bs4.BeautifulSoup")
    def test_scrape_articles(self, mock_soup, mock_requests):
        mock_requests.return_value.text = "<html></html>"
        mock_soup.return_value = MagicMock()

        # Mock parsing behavior
        mock_soup.return_value.find.return_value.string = '{"sections": []}'
        result = mock_soup.return_value.find.return_value

        # Simulate call
        result = BeautifulSoup(mock_requests.return_value.text, "html.parser")
        self.assertIsNotNone(result)


class TestCLI(unittest.TestCase):

    @patch("subprocess.run")
    def test_main(self, mock_run):
        cli.main()

        mock_run.assert_has_calls([
            call(["python", "get_bbc_news.py"], check=True),
            call(["python", "upload_articles.py"], check=True),
            call(["python", "level_articles.py"], check=True),
        ])


if __name__ == "__main__":
    unittest.main()
