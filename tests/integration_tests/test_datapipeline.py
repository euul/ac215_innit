import os
import unittest
from unittest.mock import patch, MagicMock
from pandas.testing import assert_frame_equal
import pandas as pd
import tempfile

# Add the directory containing preprocess and dataloader to the Python path
import sys
# Ensure /app is in the Python path
sys.path.insert(0, '/app')

# Import the functions to be tested
from preprocess import (
    get_filepaths, combine_jsons, data_clean, make_dataset, upload_to_gcs, split_dataset
)
from dataloader import read_json_from_gcp


class TestPreprocess(unittest.TestCase):

    @patch("preprocess.os.walk")
    def test_get_filepaths(self, mock_os_walk):
        mock_os_walk.return_value = [
            ("/data", ["subdir"], ["file1.json", "file2.txt"]),
            ("/data/subdir", [], ["file3.json"]),
        ]
        filepaths = get_filepaths("/data")
        self.assertEqual(filepaths, ["/data/file1.json", "/data/file2.txt", "/data/subdir/file3.json"])

    @patch("preprocess.pd.read_json")
    @patch("preprocess.get_filepaths")
    def test_combine_jsons(self, mock_get_filepaths, mock_read_json):
        mock_get_filepaths.return_value = ["/data/file1.json", "/data/file2.json"]
        mock_read_json.side_effect = [
            pd.DataFrame({"key": ["value1"]}),
            pd.DataFrame({"key": ["value2"]}),
        ]

        combined_df = combine_jsons("/data")
        self.assertEqual(len(combined_df), 2)
        self.assertIn("key", combined_df.columns)
        mock_read_json.assert_any_call("/data/file1.json", lines=True)
        mock_read_json.assert_any_call("/data/file2.json", lines=True)

    def test_data_clean(self):
        df = pd.DataFrame({"Label": ["A", "B", "RemoveMe"]})
        cleaned_df = data_clean(df, "Label", "RemoveMe")
        self.assertEqual(len(cleaned_df), 2)
        self.assertNotIn("RemoveMe", cleaned_df["Label"].values)

        with self.assertRaises(ValueError):
            data_clean(df, "NonExistent", "A")

        with self.assertRaises(ValueError):
            data_clean(df, "Label", "NonExistentValue")

    @patch("preprocess.Dataset.from_pandas")
    def test_make_dataset(self, mock_from_pandas):
        mock_dataset = MagicMock()
        mock_dataset.map.return_value = mock_dataset
        mock_dataset.cast_column.return_value = mock_dataset
        mock_from_pandas.return_value = mock_dataset

        df = pd.DataFrame({"Transcript": ["text1", "text2"], "Label": ["A", "B"]})
        dataset = make_dataset(df)

        # Extract the actual DataFrame passed to Dataset.from_pandas
        actual_df = mock_from_pandas.call_args[0][0]

        # Expected DataFrame
        expected_df = df[["Transcript", "Label"]]

        # Compare DataFrames
        assert_frame_equal(actual_df, expected_df)

        # Check additional interactions with the mock dataset
        mock_dataset.map.assert_called()
        mock_dataset.cast_column.assert_called_once_with("label", unittest.mock.ANY)

    @patch("preprocess.storage.Client")
    @patch("preprocess.os.walk")
    def test_upload_to_gcs(self, mock_os_walk, mock_storage_client):
        mock_os_walk.return_value = [("/source_dir", [], ["file1.txt", "file2.txt"])]
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        upload_to_gcs("test_bucket", "/source_dir", "destination_dir")
        mock_blob.upload_from_filename.assert_any_call(os.path.join("/source_dir", "file1.txt"))
        mock_blob.upload_from_filename.assert_any_call(os.path.join("/source_dir", "file2.txt"))

    def test_single_save_to_disk(self):
        # Mock dataset
        train = MagicMock()

        # Add save_to_disk behavior
        train.save_to_disk = MagicMock()

        # Create a dummy directory
        temp_dir = '/tmp/test_dir/'

        # Simulate calling save_to_disk
        train.save_to_disk(temp_dir + 'train_dataset')

        # Assert save_to_disk was called correctly
        train.save_to_disk.assert_called_once_with(temp_dir + 'train_dataset')



class TestDataloader(unittest.TestCase):

    @patch("dataloader.storage.Client")
    def test_read_json_from_gcp(self, mock_storage_client):
        mock_blob = MagicMock()
        mock_blob.download_as_text.return_value = '{"key1": "value1", "key2": "value2"}'
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            save_path = temp_file.name

        try:
            read_json_from_gcp("test_bucket", "test_blob.json", save_path)
            mock_storage_client.assert_called_once()
            mock_storage_client.return_value.bucket.assert_called_once_with("test_bucket")
            mock_bucket.blob.assert_called_once_with("test_blob.json")
            mock_blob.download_as_text.assert_called_once()

            with open(save_path, "r") as f:
                content = f.read()
                self.assertEqual(content, '{"key1": "value1", "key2": "value2"}')

        finally:
            os.remove(save_path)


if __name__ == "__main__":
    unittest.main()
