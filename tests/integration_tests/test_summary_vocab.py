import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import sys
import re
import io

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from summary_vocab_news import (
    read_json_from_gcp as read_json_from_gcp_sum,
    create_prompt as create_prompt_sum,
    upload_to_gcp as upload_to_gcp_sum,
    save_prompts_to_jsonl,
    submit_batch_prediction,
    load_local_data,
    add_unique_ids_to_data
)

from extract_results_news import (
    read_json_from_gcp as read_json_from_gcp_extract,
    download_jsonl_from_gcp,
    upload_to_gcp as upload_to_gcp_extract
)

from summary_vocab_yt import (
    read_json_from_gcp as read_json_from_gcp_sum_yt,
    create_prompt as create_prompt_sum_yt
)

from extract_results_yt import (
    read_json_from_gcp as read_json_from_gcp_extract_yt,
    download_jsonl_from_gcp as download_jsonl_from_gcp_extract_yt,
    read_predictions_from_jsonl as read_predictions_from_jsonl_yt,
    update_local_json,
    upload_and_sync_selected_folders
)



class TestSummaryVocabNews(unittest.TestCase):
    
    @patch('summary_vocab_news.storage.Client')
    def test_read_json_from_gcp_sum(self, mock_storage_client):
        """Test reading JSON file from GCP bucket."""
        # Mock bucket and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Call the function
        bucket_name = "test_bucket"
        input_file_path = "path/to/input.json"
        local_file_path = "local_input.json"
        
        read_json_from_gcp_sum(bucket_name, input_file_path, local_file_path)

        # Assert calls
        mock_storage_client.return_value.bucket.assert_called_with(bucket_name)
        mock_bucket.blob.assert_called_with(input_file_path)
        mock_blob.download_to_filename.assert_called_with(local_file_path)

    def test_create_prompt(self):
        """Test creating a prompt from input data."""
        data = {
            "id": 1,
            "Text": "This is a test article."
        }
        expected_prompt_start = "ID: 1\nPlease summarize the following content"
        expected_prompt_contains = "<vocab>\nA1: word1, word2, word3"
        
        prompt = create_prompt_sum(data)

        # Check prompt starts and contains key instructions
        self.assertTrue(prompt.startswith(expected_prompt_start))
        self.assertIn(expected_prompt_contains, prompt)
        self.assertIn("This is a test article.", prompt)

    @patch('summary_vocab_news.storage.Client')
    def test_upload_to_gcp_sum(self, mock_storage_client):
        """Test uploading file to GCP bucket."""
        # Mock bucket and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Mock the `get_bucket` method to return the mocked bucket
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Call the function
        bucket_name = "test_bucket"
        destination_blob_path = "path/to/upload.json"
        source_file_path = "test_file.json"
        
        # Create a dummy file
        with open(source_file_path, 'w') as f:
            f.write("dummy content")

        upload_to_gcp_sum(bucket_name, destination_blob_path, source_file_path)

        # Assert calls
        mock_storage_client.return_value.get_bucket.assert_called_with(bucket_name)
        mock_bucket.blob.assert_called_with(destination_blob_path)
        mock_blob.upload_from_filename.assert_called_with(source_file_path)

        # Clean up
        os.remove(source_file_path)


    def test_jsonl_output_format(self):
        """Test JSONL output format."""
        data_with_ids = [
            {"id": 0, "Text": "Article 1 content."},
            {"id": 1, "Text": "Article 2 content."}
        ]

        prompts = [create_prompt_sum_yt(content['Text'], content['id']) for content in data_with_ids]
        
        # Ensure that each prompt is correctly formatted
        for prompt in prompts:
            self.assertIn("<vocab>", prompt)
            self.assertIn("<questions>", prompt)

    # @patch('summary_vocab_news.vertexai.BatchPredictionJob.submit')
    # def test_batch_prediction_submission(self, mock_submit):
    #     """Test submitting a batch prediction job."""
    #     # Mock the job response
    #     mock_job = MagicMock()
    #     mock_submit.return_value = mock_job
        
    #     input_data = "gs://innit_articles_bucket/bbc_news/news_inputs.jsonl"
    #     output_url = "gs://innit_articles_bucket/bbc_news_output"

    #     job = submit_batch_prediction(input_data, output_url)

    #     # Assert the batch prediction job submission
    #     mock_submit.assert_called_with(
    #         source_model="gemini-1.5-pro-002", input_dataset=input_data, output_uri_prefix=output_url
    #     )
    #     self.assertEqual(job, mock_job)

    def test_local_file_reading(self):
        """Test local JSON file reading."""
        local_file_path = "test_articles.json"
        test_data = [
            {"Text": "Sample article 1"},
            {"Text": "Sample article 2"}
        ]
        
        # Create a dummy JSON file
        with open(local_file_path, 'w') as f:
            json.dump(test_data, f)

        # Read the file using the function
        data = load_local_data(local_file_path)

        self.assertEqual(data, [test_data])

        # Clean up
        os.remove(local_file_path)

    def test_add_unique_ids_to_data(self):
        """Test adding unique IDs to data."""
        data = [
            {"Text": "Article 1"},
            {"Text": "Article 2"}
        ]
        data_with_ids = add_unique_ids_to_data(data)

        # Ensure each entry has a unique id
        self.assertEqual(len(data_with_ids), 2)
        self.assertEqual(data_with_ids[0]["id"], 0)
        self.assertEqual(data_with_ids[1]["id"], 1)

    @patch('summary_vocab_news.storage.Client')
    def test_save_prompts_to_jsonl(self, mock_storage_client):
        """Test saving prompts to JSONL."""
        prompts = [
            "ID: 0\nPlease summarize the following content",
            "ID: 1\nPlease summarize the following content"
        ]
        save_prompts_to_jsonl(prompts, "test_output.jsonl")

        # Assert file creation
        self.assertTrue(os.path.exists("test_output.jsonl"))
        
        # Clean up
        os.remove("test_output.jsonl")

class TestExtractResultsNews(unittest.TestCase):

    @patch('extract_results_news.storage.Client')
    def test_read_json_from_gcp_extract(self, mock_storage_client):
        """Test reading JSON file from GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test_bucket"
        input_file_path = "path/to/input.json"
        local_file_path = "local_test.json"

        read_json_from_gcp_extract(bucket_name, input_file_path, local_file_path)

        mock_storage_client.return_value.bucket.assert_called_with(bucket_name)
        mock_bucket.blob.assert_called_with(input_file_path)
        mock_blob.download_to_filename.assert_called_with(local_file_path)

    @patch('extract_results_news.storage.Client')
    def test_download_jsonl_from_gcp(self, mock_storage_client):
        """Test downloading JSONL file from GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()

        # Mock the blob with a folder starting with "prediction-model-"
        mock_blob.name = "prediction-model-2024-12-04T20:56:36.740413Z/test.jsonl"
        
        # Mock the client methods
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test_bucket"
        directory_prefix = "test_prefix"
        local_file_path = "test_local.jsonl"
        
        # Call the method
        download_jsonl_from_gcp(bucket_name, directory_prefix, local_file_path)
        
        # Ensure the list_blobs method was called with the correct prefix
        mock_bucket.list_blobs.assert_called_with(prefix=directory_prefix)
        
        # Ensure download_to_filename is called with the correct file path
        mock_blob.download_to_filename.assert_called_with(local_file_path)

    @patch('extract_results_news.storage.Client')
    def test_upload_to_gcp_extract(self, mock_storage_client):
        """Test uploading data to GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        bucket_name = "test_bucket"
        folder_prefix = "test_folder"
        file_name = "test_file"
        data = {"key": "value"}

        upload_to_gcp_extract(bucket_name, folder_prefix, file_name, data)

        expected_blob_path = f"{folder_prefix}/{file_name}.json"
        mock_bucket.blob.assert_called_with(expected_blob_path)
        mock_blob.upload_from_string.assert_called_with(
            json.dumps(data, indent=4), content_type="application/json"
        )


    def test_prediction_parsing(self):
        """Test parsing predictions from JSONL."""
        predictions = [
            {
                "request": {
                    "contents": [
                        {"parts": [{"text": "ID: 1"}]}
                    ]
                },
                "response": {
                    "candidates": [
                        {"content": {"parts": [{"text": "<sum>Test summary</sum><vocab>Test vocab</vocab><questions>Test questions</questions>"}]}}
                    ]
                }
            }
        ]

        pred_dict = {}
        for prediction in predictions:
            request = prediction['request']['contents'][0]['parts'][0]['text']
            response = prediction['response']['candidates'][0]['content']['parts'][0]['text']
            id_match = re.search(r"ID:\s*(\d+)", request)
            if id_match:
                item_id = int(id_match.group(1))
                pred_dict[item_id] = response

        self.assertIn(1, pred_dict)
        self.assertIn("<sum>Test summary</sum>", pred_dict[1])
        self.assertIn("<vocab>Test vocab</vocab>", pred_dict[1])
        self.assertIn("<questions>Test questions</questions>", pred_dict[1])


class TestSummaryVocabYT(unittest.TestCase):

    @patch('summary_vocab_yt.storage.Client')
    def test_read_json_from_gcp(self, mock_storage_client):
        """Test reading JSON data from GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [
            MagicMock(name="yt_transcripts/A1/file1.json"),
            MagicMock(name="yt_transcripts/A1/file2.json"),
        ]

        read_json_from_gcp_sum_yt()

        mock_storage_client.return_value.bucket.assert_called_with("innit_articles_bucket")
        mock_bucket.list_blobs.assert_called()
        self.assertEqual(mock_bucket.list_blobs.call_count, len(["A1", "A2", "B1", "B2", "C1"]))

    def test_create_prompt(self):
        """Test prompt creation with content and ID."""
        content = "This is a sample transcript text."
        id = 1
        prompt = create_prompt_sum_yt(content, id)

        self.assertIn("ID: 1", prompt)
        self.assertIn("Please summarize the following content", prompt)
        self.assertIn(content, prompt)
        self.assertIn("<sum>", prompt)
        self.assertIn("<vocab>", prompt)
        self.assertIn("<questions>", prompt)

class TestExtractResultsYT(unittest.TestCase):

    @patch('extract_results_yt.storage.Client')
    def test_read_json_from_gcp(self, mock_storage_client):
        """Test reading JSON files from GCP bucket."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [
            MagicMock(name="yt_transcripts/A1/file1.json"),
            MagicMock(name="yt_transcripts/A1/file2.json"),
        ]

        read_json_from_gcp_extract_yt()

        mock_storage_client.return_value.bucket.assert_called_with("innit_articles_bucket")
        mock_bucket.list_blobs.assert_called()
        self.assertEqual(mock_bucket.list_blobs.call_count, len(["A1", "A2", "B1", "B2", "C1"]))

    @patch('extract_results_yt.storage.Client')
    def test_download_jsonl_from_gcp(self, mock_storage_client):
        """Test downloading JSONL file from GCP bucket."""
        # Create mock objects for bucket and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Configure the mock storage client to return the mock bucket
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Set the name of the blob to match the expected folder structure and name
        mock_blob.name = "prediction-model-folder/summary_vocab.jsonl"
        
        # Configure the mock bucket to return a list of blobs that includes the file we want
        mock_bucket.list_blobs.return_value = [mock_blob]
        
        # Configure the mock bucket to return the mock blob when requested
        mock_bucket.blob.return_value = mock_blob
        
        # Set test parameters
        bucket_name = "test_bucket"
        directory_prefix = "yt_transcripts/A1"
        local_file_path = "yt_transcripts/A1/summary_vocab.jsonl"
        
        # Call the function under test
        download_jsonl_from_gcp_extract_yt(bucket_name, directory_prefix, local_file_path)
        
        # Assert the correct call was made to download the file
        mock_bucket.list_blobs.assert_called_with(prefix=directory_prefix)
        mock_blob.download_to_filename.assert_called_with(local_file_path)

    def test_read_predictions_from_jsonl(self):
        """Test reading predictions from a JSONL file."""
        test_jsonl_content = [
            json.dumps({
                "request": {
                    "contents": [{"parts": [{"text": "ID: 1"}]}]
                },
                "response": {
                    "candidates": [
                        {"content": {"parts": [{"text": "<sum>Summary</sum><vocab>Vocab</vocab>"}]}}
                    ]
                }
            }),
            json.dumps({
                "request": {
                    "contents": [{"parts": [{"text": "ID: 2"}]}]
                },
                "response": {
                    "candidates": [
                        {"content": {"parts": [{"text": "<sum>Another Summary</sum><vocab>Another Vocab</vocab>"}]}}
                    ]
                }
            })
        ]

        with patch("builtins.open", mock_open(read_data="\n".join(test_jsonl_content))):
            pred_dict = read_predictions_from_jsonl_yt("test_file.jsonl")

        self.assertEqual(pred_dict[1], "<sum>Summary</sum><vocab>Vocab</vocab>")
        self.assertEqual(pred_dict[2], "<sum>Another Summary</sum><vocab>Another Vocab</vocab>")



if __name__ == "__main__":
    unittest.main()
