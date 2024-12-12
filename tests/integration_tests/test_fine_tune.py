import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import json
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
import sys
# Ensure /app is in the Python path
sys.path.insert(0, '/app')

import finetune
import make_dataset
import sweep_lr

class TestFinetune(unittest.TestCase):

    @patch("finetune.storage.Client")
    def test_download_weights(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        finetune.download_weights("test_bucket", "test_blob", "local_model_path.pth")

        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_blob")
        mock_blob.download_to_filename.assert_called_once_with("local_model_path.pth")

    @patch("torch.load")
    @patch("finetune.AutoModelForSequenceClassification.from_pretrained")
    def test_load_model(self, mock_from_pretrained, mock_load):
        mock_model = Mock(spec=AutoModelForSequenceClassification)
        mock_model.load_state_dict = Mock()
        mock_model.eval = Mock()
        mock_model.deberta = Mock()
        mock_model.deberta.parameters = Mock(return_value=iter([]))  # Mock parameters as an iterable
        mock_from_pretrained.return_value = mock_model

        model = finetune.load_model("local_model_path.pth", 5)

        mock_from_pretrained.assert_called_once_with(
            "microsoft/deberta-v3-small", num_labels=5
        )
        mock_load.assert_called_once_with(
            "local_model_path.pth", map_location=torch.device("cpu")
        )
        mock_model.load_state_dict.assert_called_once()
        mock_model.eval.assert_called_once()
        self.assertEqual(model, mock_model)

    @patch("finetune.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_download_dataset_folder(self, mock_exists, mock_makedirs, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "test_blob_file"
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        finetune.download_dataset_folder("test_bucket", "test_blob_prefix", "./datasets")

        mock_storage_client.assert_called_once()
        mock_bucket.list_blobs.assert_called_once_with(prefix="test_blob_prefix")
        mock_blob.download_to_filename.assert_called_once_with("./datasets/test_blob_file")

    @patch("finetune.load_from_disk")
    def test_load_datasets(self, mock_load_from_disk):
        mock_train, mock_valid, mock_test = Mock(), Mock(), Mock()
        mock_load_from_disk.side_effect = [mock_train, mock_valid, mock_test]

        train, valid, test = finetune.load_datasets(
            "./datasets", "train/", "valid/", "test/"
        )

        self.assertEqual(train, mock_train)
        self.assertEqual(valid, mock_valid)
        self.assertEqual(test, mock_test)
        self.assertEqual(len(mock_load_from_disk.mock_calls), 3)


class TestMakeDataset(unittest.TestCase):

    @patch("make_dataset.storage.Client")
    @patch("os.walk", return_value=[("./local_dir", [], ["file.txt"])])
    def test_upload_to_gcs(self, mock_walk, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        make_dataset.upload_to_gcs("test_bucket", "./local_dir", "dest_dir")

        mock_bucket.blob.assert_called_once_with("dest_dir/file.txt")
        mock_blob.upload_from_filename.assert_called_once_with("./local_dir/file.txt")




class TestSweepLR(unittest.TestCase):

    @patch("sweep_lr.storage.Client")
    def test_download_weights(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        sweep_lr.download_weights("test_bucket", "test_blob", "local_model_path.pth")

        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_blob")
        mock_blob.download_to_filename.assert_called_once_with("local_model_path.pth")

    @patch("torch.load")
    @patch("sweep_lr.AutoModelForSequenceClassification.from_pretrained")
    def test_load_model(self, mock_from_pretrained, mock_load):
        mock_model = Mock(spec=AutoModelForSequenceClassification)
        mock_model.load_state_dict = Mock()
        mock_model.eval = Mock()
        mock_model.deberta = Mock()
        mock_model.deberta.parameters = Mock(return_value=iter([]))  # Mock parameters as an iterable
        mock_from_pretrained.return_value = mock_model

        model = sweep_lr.load_model("local_model_path.pth", 5)

        mock_from_pretrained.assert_called_once_with(
            "microsoft/deberta-v3-small", num_labels=5
        )
        mock_load.assert_called_once_with(
            "local_model_path.pth", map_location=torch.device("cpu")
        )
        mock_model.load_state_dict.assert_called_once()
        mock_model.eval.assert_called_once()
        self.assertEqual(model, mock_model)


    @patch("sweep_lr.load_from_disk")
    def test_load_datasets(self, mock_load_from_disk):
        mock_train, mock_valid, mock_test = Mock(), Mock(), Mock()
        mock_load_from_disk.side_effect = [mock_train, mock_valid, mock_test]

        train, valid, test = sweep_lr.load_datasets(
            "./datasets", "train/", "valid/", "test/"
        )

        self.assertEqual(train, mock_train)
        self.assertEqual(valid, mock_valid)
        self.assertEqual(test, mock_test)
        self.assertEqual(len(mock_load_from_disk.mock_calls), 3)


if __name__ == "__main__":
    unittest.main()
