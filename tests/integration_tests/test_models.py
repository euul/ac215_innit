import unittest
from unittest.mock import patch, MagicMock, call
import os
import torch
import argparse
import sys

# Ensure the correct module path is added
sys.path.insert(0, '/app')  # Update with the correct path if necessary

from train_model import download_dataset_folder, load_datasets, upload_blob, main


class TestScript(unittest.TestCase):

    @patch('train_model.storage.Client')
    @patch('train_model.os.makedirs')
    @patch('train_model.os.path.exists')
    def test_download_dataset_folder(self, mock_exists, mock_makedirs, mock_storage_client):
        # Mock input arguments
        bucket_name = "test_bucket"
        blob_prefix = "test_prefix/"
        local_dataset_dir = "./test_datasets"

        # Mock GCP bucket and blobs
        mock_blob = MagicMock()
        mock_blob.name = "test_prefix/test_blob.json"
        mock_bucket = MagicMock()
        mock_bucket.list_blobs.return_value = [mock_blob]

        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_exists.side_effect = [False]  # Simulate directory not existing

        # Call function
        download_dataset_folder(bucket_name, blob_prefix, local_dataset_dir)

        # Verify os.makedirs was called
        mock_makedirs.assert_called_with('./test_datasets/test_prefix', exist_ok=True)

        # Verify bucket and blobs were accessed
        mock_storage_client.assert_called_once()
        mock_bucket.list_blobs.assert_called_once_with(prefix=blob_prefix)
        mock_blob.download_to_filename.assert_called_once_with(
            os.path.join(local_dataset_dir, mock_blob.name)
        )

    @patch('train_model.load_from_disk')
    @patch('train_model.TRAIN_BLOB_PREFIX', 'train_dataset/')
    @patch('train_model.VALID_BLOB_PREFIX', 'valid_dataset/')
    @patch('train_model.TEST_BLOB_PREFIX', 'test_dataset/')
    def test_load_datasets(self, mock_load_from_disk):
        # Mock input arguments
        local_dataset_dir = "./test_datasets"

        # Mock datasets
        mock_train_dataset = MagicMock()
        mock_valid_dataset = MagicMock()
        mock_test_dataset = MagicMock()
        mock_load_from_disk.side_effect = [
            mock_train_dataset,
            mock_valid_dataset,
            mock_test_dataset
        ]

        # Call function
        train_dataset, valid_dataset, test_dataset = load_datasets(local_dataset_dir)

        # Verify datasets are loaded correctly
        self.assertEqual(train_dataset, mock_train_dataset)
        self.assertEqual(valid_dataset, mock_valid_dataset)
        self.assertEqual(test_dataset, mock_test_dataset)

        # Verify calls to load_from_disk
        mock_load_from_disk.assert_has_calls([
            call(os.path.join(local_dataset_dir, "train_dataset")),
            call(os.path.join(local_dataset_dir, "valid_dataset")),
            call(os.path.join(local_dataset_dir, "test_dataset"))
        ])

    @patch('train_model.storage.Client')
    def test_upload_blob(self, mock_storage_client):
        # Mock input arguments
        bucket_name = "test_bucket"
        source_file_name = "test_model.pth"
        destination_blob_name = "test_blob.pth"

        # Mock GCP client, bucket, and blob
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        # Call function
        upload_blob(bucket_name, source_file_name, destination_blob_name)

        # Verify bucket and blob interactions
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with(destination_blob_name)
        mock_blob.upload_from_filename.assert_called_once_with(source_file_name)

    @patch('train_model.wandb.finish')  # Mock wandb.finish
    @patch('train_model.upload_blob')
    @patch('train_model.Trainer.evaluate')
    @patch('train_model.Trainer.train')
    @patch('train_model.wandb.init')
    @patch('train_model.wandb.login')
    @patch('train_model.load_datasets')
    @patch('train_model.download_dataset_folder')
    @patch('train_model.AutoTokenizer.from_pretrained')
    @patch('train_model.AutoModelForSequenceClassification.from_pretrained')
    @patch('train_model.argparse.ArgumentParser.parse_args')
    def test_main(
        self,
        mock_parse_args,
        mock_model_from_pretrained,
        mock_tokenizer_from_pretrained,
        mock_download_dataset_folder,
        mock_load_datasets,
        mock_wandb_login,
        mock_wandb_init,
        mock_trainer_train,
        mock_trainer_evaluate,
        mock_upload_blob,
        mock_wandb_finish
    ):
        # Mock parsed arguments
        mock_parse_args.return_value = argparse.Namespace(wandb_key='fake_wandb_key')

        # Mock dataset features
        mock_train_dataset = MagicMock()
        mock_train_dataset.features = {'label': MagicMock(num_classes=5)}
        mock_valid_dataset = MagicMock()
        mock_test_dataset = MagicMock()
        mock_load_datasets.return_value = (mock_train_dataset, mock_valid_dataset, mock_test_dataset)

        # Mock the tokenizer and model
        mock_tokenizer = MagicMock()
        mock_model = MagicMock(spec=torch.nn.Module)  # Ensure the model inherits torch.nn.Module
        mock_tokenizer_from_pretrained.return_value = mock_tokenizer
        mock_model_from_pretrained.return_value = mock_model

        # Mock Trainer methods
        mock_trainer_train.return_value = None
        mock_trainer_evaluate.return_value = {'accuracy': 95.0}

        # Fix `num_labels` to match expectation
        mock_model_from_pretrained.return_value.num_labels = 5

        # Run main
        with patch('train_model.torch.save') as mock_torch_save:
            main()

            # Assertions for argument parsing
            mock_parse_args.assert_called_once()

            # Assertions for dataset download
            mock_download_dataset_folder.assert_any_call('innit_articles_bucket', 'train_dataset/', './datasets')
            mock_download_dataset_folder.assert_any_call('innit_articles_bucket', 'valid_dataset/', './datasets')
            mock_download_dataset_folder.assert_any_call('innit_articles_bucket', 'test_dataset/', './datasets')

            # Assertions for dataset loading
            mock_load_datasets.assert_called_once_with('./datasets')

            # Assertions for tokenizer and model loading
            mock_tokenizer_from_pretrained.assert_called_once_with("microsoft/deberta-v3-small")
            mock_model_from_pretrained.assert_called_once_with(
                "microsoft/deberta-v3-small",
                num_labels=5
            )

            # Assertions for W&B
            mock_wandb_login.assert_called_once_with(key='fake_wandb_key')
            mock_wandb_init.assert_called_once_with(
                project="innit-baseline-experiments",
                name="lr_2e_5"
            )

            # Assertions for Trainer
            mock_trainer_train.assert_called_once()
            mock_trainer_evaluate.assert_called_once_with(mock_test_dataset)

            # Assertions for model saving and upload
            mock_torch_save.assert_called_once_with(mock_model.state_dict(), 'distill_bert_c1_weights.pth')
            mock_upload_blob.assert_called_once_with(
                'innit_articles_bucket',
                'distill_bert_c1_weights.pth',
                'distill_bert_c1_weights.pth'
            )


if __name__ == '__main__':
    unittest.main()
