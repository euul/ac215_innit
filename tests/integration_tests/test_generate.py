import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from download_train_datasets import download_dataset_folder


class TestDownloadTrainDatasets(unittest.TestCase):

    @patch("download_train_datasets.storage.Client")
    @patch("os.path.exists")
    def test_skip_download_if_exists(self, mock_exists, mock_storage_client):
        """Test skipping download if the dataset folder already exists locally."""
        # Mock the local path existence check
        mock_exists.return_value = True

        # Call the function
        download_dataset_folder("test_bucket", "train_dataset/", "./datasets")

        # Assert no GCP interactions occurred
        mock_storage_client.assert_not_called()

    @patch("download_train_datasets.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_create_nested_directories(self, mock_exists, mock_makedirs, mock_storage_client):
        """Test creation of nested directories for downloading blobs."""
        # Mock the local path existence check
        mock_exists.side_effect = lambda path: False

        # Mock the GCP storage client, bucket, and blobs
        mock_blob = MagicMock()
        mock_blob.name = "train_dataset/nested/file.json"  # Explicitly set the blob name
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [mock_blob]

        # Call the function
        download_dataset_folder("test_bucket", "train_dataset/", "./datasets")

        # Assert local nested directory creation
        mock_makedirs.assert_any_call("./datasets/train_dataset/nested", exist_ok=True)

        # Assert blob download
        mock_blob.download_to_filename.assert_called_once_with("./datasets/train_dataset/nested/file.json")



if __name__ == "__main__":
    unittest.main()
