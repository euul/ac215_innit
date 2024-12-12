import unittest
from unittest.mock import patch, MagicMock
import json
import random
import sys

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from gen_test import (
    get_gcp_client,
    fetch_questions_from_gcp,
    upload_to_gcp,
    main
)

class TestGenTest(unittest.TestCase):

    @patch('gen_test.storage.Client')
    def test_get_gcp_client(self, mock_storage_client):
        """Test Google Cloud Storage client initialization."""
        client = get_gcp_client()
        mock_storage_client.assert_called_once_with(project="innit-437518")
        self.assertEqual(client, mock_storage_client.return_value)

    @patch('gen_test.storage.Client')
    def test_fetch_questions_from_gcp(self, mock_storage_client):
        """Test fetching questions from GCP."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock blob behavior
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps([
            {"question": "Question 1?", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question 2?", "choices": ["A", "B", "C"], "answer": "B"}
        ])

        client = get_gcp_client()
        level = "A1"
        questions = fetch_questions_from_gcp(client, level)

        mock_storage_client.return_value.get_bucket.assert_called_with("innit_articles_bucket")
        mock_bucket.blob.assert_called_with(f"generated_questions/generated_questions_{level}.json")
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["question"], "Question 1?")

    @patch('gen_test.storage.Client')
    def test_fetch_questions_from_gcp_file_not_found(self, mock_storage_client):
        """Test handling of missing GCP file."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock blob behavior for non-existent file
        mock_blob.exists.return_value = False

        client = get_gcp_client()
        level = "A1"

        with self.assertRaises(FileNotFoundError):
            fetch_questions_from_gcp(client, level)

    @patch('gen_test.storage.Client')
    def test_upload_to_gcp(self, mock_storage_client):
        """Test uploading data to GCP."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        client = get_gcp_client()
        data = [{"question": "Sample Question", "choices": ["A", "B", "C"], "answer": "A"}]
        destination_blob_name = "test_output.json"

        upload_to_gcp(client, data, destination_blob_name)

        mock_storage_client.return_value.get_bucket.assert_called_with("innit_articles_bucket")
        mock_bucket.blob.assert_called_with(destination_blob_name)
        mock_blob.upload_from_string.assert_called_with(
            data=json.dumps(data, indent=4),
            content_type='application/json'
        )

    @patch('gen_test.fetch_questions_from_gcp')
    @patch('gen_test.upload_to_gcp')
    @patch('gen_test.get_gcp_client')
    def test_main(self, mock_get_client, mock_upload, mock_fetch_questions):
        """Test the main function."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_fetch_questions.side_effect = lambda client, level: [
            {"question": f"Question {level} - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": f"Question {level} - 2", "choices": ["A", "B", "C"], "answer": "B"},
            {"question": f"Question {level} - 3", "choices": ["A", "B", "C"], "answer": "C"},
        ]

        with patch('random.sample', side_effect=lambda x, k: x[:k]):
            main()

        # Verify fetch_questions_from_gcp is called for each level
        for level in ["A1", "A2", "B1", "B2", "C1"]:
            mock_fetch_questions.assert_any_call(mock_client, level)

        # Verify upload_to_gcp is called with combined test data
        combined_test = [
            {"question": "Question A1 - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question A1 - 2", "choices": ["A", "B", "C"], "answer": "B"},
            {"question": "Question A2 - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question A2 - 2", "choices": ["A", "B", "C"], "answer": "B"},
            {"question": "Question B1 - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question B1 - 2", "choices": ["A", "B", "C"], "answer": "B"},
            {"question": "Question B2 - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question B2 - 2", "choices": ["A", "B", "C"], "answer": "B"},
            {"question": "Question C1 - 1", "choices": ["A", "B", "C"], "answer": "A"},
            {"question": "Question C1 - 2", "choices": ["A", "B", "C"], "answer": "B"},
        ]
        mock_upload.assert_called_once_with(mock_client, combined_test, "generated_questions/diagnostic_test.json")

if __name__ == "__main__":
    unittest.main()
