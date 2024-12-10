import os
import unittest
from unittest.mock import patch, Mock, MagicMock
from google.cloud import storage
from datasets import Dataset
import shutil
import tempfile
import json
import numpy as np
import torch
import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

import infer_model as infer
import load_datasets as load_ds
import train_model as train

class TestInferModel(unittest.TestCase):

    @patch("infer_model.storage.Client")
    def test_download_weights(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        infer.download_weights("test_bucket", "test_blob", "test_model_path.pth")
        
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_blob")
        mock_blob.download_to_filename.assert_called_once_with("test_model_path.pth")

    @patch("infer_model.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_download_dataset_folder(self, mock_exists, mock_makedirs, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "test_blob_file"
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        infer.download_dataset_folder("test_bucket", "test_blob_prefix", "./datasets")
        
        mock_storage_client.assert_called_once()
        mock_bucket.list_blobs.assert_called_once_with(prefix="test_blob_prefix")
        mock_blob.download_to_filename.assert_called_once_with("./datasets/test_blob_file")


    @patch("torch.load")
    @patch("infer_model.AutoModelForSequenceClassification.from_pretrained")
    def test_load_model(self, mock_from_pretrained, mock_load):
        mock_model = Mock(spec=AutoModelForSequenceClassification)
        mock_model.load_state_dict = Mock()  # Mock load_state_dict
        mock_model.eval = Mock()  # Mock eval method
        mock_from_pretrained.return_value = mock_model

        model = infer.load_model("test_model_path.pth", 5)

        mock_from_pretrained.assert_called_once_with(
            "microsoft/deberta-v3-small", num_labels=5
        )
        mock_load.assert_called_once_with("test_model_path.pth", map_location=torch.device("cpu"))
        mock_model.load_state_dict.assert_called_once()  # Verify load_state_dict is called
        mock_model.eval.assert_called_once()  # Verify eval is called
        self.assertEqual(model, mock_model)



    @patch("infer_model.AutoTokenizer.from_pretrained")
    def test_infer(self, mock_tokenizer):
        mock_model = Mock()
        mock_dataset = Mock()
        
        # Mock the tokenizer and dataset
        mock_tokenizer.return_value = Mock()
        mock_dataset.map.return_value = {
            "input_ids": [[1, 2, 3]],
            "attention_mask": [[1, 1, 1]],
        }
        mock_model.return_value = Mock(logits=torch.tensor([[0.1, 0.9]]))

        predictions = infer.infer(mock_model, mock_dataset)

        self.assertTrue(torch.equal(predictions, torch.tensor([1])))


class TestLoadDatasets(unittest.TestCase):

    @patch("load_datasets.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_download_dataset_folder(self, mock_exists, mock_makedirs, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "test_blob_file"
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        load_ds.download_dataset_folder("test_bucket", "test_blob_prefix", "./datasets")
        
        mock_storage_client.assert_called_once()
        mock_bucket.list_blobs.assert_called_once_with(prefix="test_blob_prefix")
        mock_blob.download_to_filename.assert_called_once_with("./datasets/test_blob_file")

    @patch("load_datasets.load_from_disk")
    def test_load_datasets(self, mock_load_from_disk):
        mock_load_from_disk.side_effect = [Mock(), Mock(), Mock()]
        
        train_dataset, valid_dataset, test_dataset = load_ds.load_datasets("./datasets")
        
        self.assertEqual(len(mock_load_from_disk.mock_calls), 3)
        self.assertIsNotNone(train_dataset)
        self.assertIsNotNone(valid_dataset)
        self.assertIsNotNone(test_dataset)


class TestTrainModel(unittest.TestCase):

    @patch("train_model.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_download_dataset_folder(self, mock_exists, mock_makedirs, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "test_blob_file"
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        train.download_dataset_folder("test_bucket", "test_blob_prefix", "./datasets")
        
        mock_storage_client.assert_called_once()
        mock_bucket.list_blobs.assert_called_once_with(prefix="test_blob_prefix")
        mock_blob.download_to_filename.assert_called_once_with("./datasets/test_blob_file")

    @patch("train_model.load_from_disk")
    def test_load_datasets(self, mock_load_from_disk):
        mock_load_from_disk.side_effect = [Mock(), Mock(), Mock()]
        
        train_dataset, valid_dataset, test_dataset = train.load_datasets("./datasets")
        
        self.assertEqual(len(mock_load_from_disk.mock_calls), 3)
        self.assertIsNotNone(train_dataset)
        self.assertIsNotNone(valid_dataset)
        self.assertIsNotNone(test_dataset)

    @patch("train_model.AutoTokenizer.from_pretrained")
    def test_preprocess_function(self, mock_tokenizer):
        # Mock tokenizer behavior
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.side_effect = lambda text, truncation, padding, max_length: {
            "input_ids": [1, 2, 3],
            "attention_mask": [1, 1, 1],
        }

        # Call the function with the mocked tokenizer
        result = train.preprocess_function({"Transcript": "sample text"}, mock_tokenizer.return_value)

        # Assertions
        self.assertIn("input_ids", result)
        self.assertIn("attention_mask", result)
        self.assertEqual(result["input_ids"], [1, 2, 3])
        self.assertEqual(result["attention_mask"], [1, 1, 1])



    @patch("train_model.storage.Client")
    def test_upload_blob(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        train.upload_blob("test_bucket", "source_file.txt", "dest_blob.txt")
        
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("dest_blob.txt")
        mock_blob.upload_from_filename.assert_called_once_with("source_file.txt")


if __name__ == "__main__":
    unittest.main()