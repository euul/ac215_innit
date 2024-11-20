import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
import json
import gc
import sys
import torch
from datasets import Dataset

sys.path.insert(0, '/app')

from get_transcript import (
    get_transcript,
    clean_timestamps,
    upload_to_gcp_bucket as upload_transcripts_to_gcp,
    save_transcripts,
    cleanup_local_folder
)
from level_transcript import (
    download_transcripts,
    upload_to_gcp_bucket as upload_labeled_to_gcp,
    update_json_files_with_labels,
    TranscriptDataset,
    infer
)

from video_id_scraper import get_video_info, main


class TestGetTranscript(unittest.TestCase):
    @patch("get_transcript.YouTubeTranscriptApi.get_transcript")
    def test_get_transcript_success(self, mock_get_transcript):
        mock_get_transcript.return_value = [{"start": 3661, "text": "Hello World"}]
        transcript = get_transcript("test_video_id")
        self.assertEqual(transcript[0]['start'], "01:01:01")
        self.assertEqual(transcript[0]['text'], "Hello World")
    
    @patch("get_transcript.YouTubeTranscriptApi.get_transcript")
    def test_get_transcript_failure(self, mock_get_transcript):
        mock_get_transcript.side_effect = Exception("Transcript not found")
        transcript = get_transcript("test_video_id")
        self.assertIsNone(transcript)
    
    def test_clean_timestamps(self):
        self.assertEqual(clean_timestamps(3661), "01:01:01")
        self.assertEqual(clean_timestamps(59), "00:00:59")

    @patch("get_transcript.storage.Client")
    def test_upload_to_gcp_bucket_transcripts(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        local_folder = tempfile.mkdtemp()
        file_path = os.path.join(local_folder, "test.json")
        with open(file_path, "w") as f:
            json.dump({"test": "data"}, f)

        upload_transcripts_to_gcp("test_bucket", "test_folder", local_folder)
        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_folder/test.json")
        mock_blob.upload_from_filename.assert_called_once_with(file_path, content_type="application/json")

        cleanup_local_folder(local_folder)

    def test_cleanup_local_folder(self):
        temp_folder = tempfile.mkdtemp()
        self.assertTrue(os.path.exists(temp_folder))
        cleanup_local_folder(temp_folder)
        self.assertFalse(os.path.exists(temp_folder))

    @patch("get_transcript.get_transcript")
    def test_save_transcripts(self, mock_get_transcript):
        mock_get_transcript.return_value = [{"start": "00:00:01", "text": "Sample text"}]
        with tempfile.TemporaryDirectory() as temp_dir:
            videos = [
                {"video_name": "video1", "video_id": "123"},
                {"video_name": "video2", "video_id": "456"}
            ]
            save_transcripts(videos, temp_dir)
            for video in videos:
                file_path = os.path.join(temp_dir, f"{video['video_name']}.json")
                self.assertTrue(os.path.exists(file_path))
                with open(file_path, "r") as f:
                    data = json.load(f)
                    self.assertEqual(data["video_name"], video["video_name"])
                    self.assertEqual(data["video_id"], video["video_id"])
                    self.assertEqual(data["transcript"], [{"start": "00:00:01", "text": "Sample text"}])


class TestLevelTranscript(unittest.TestCase):
    @patch("level_transcript.storage.Client")
    def test_download_transcripts(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.name = "yt_transcripts/test.json"
        mock_blob.download_to_filename.side_effect = lambda path: open(path, 'w').close()
        mock_bucket.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        with tempfile.TemporaryDirectory() as temp_dir:
            download_transcripts("test_bucket", "yt_transcripts", temp_dir)
            mock_storage_client.assert_called_once()
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "test.json")))

    def test_transcript_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file_path = os.path.join(temp_dir, "test.json")
            with open(json_file_path, "w") as f:
                json.dump({"transcript": [{"text": "Hello World"}]}, f)

            dataset = TranscriptDataset(transcript_dir=temp_dir)
            hf_dataset = dataset.to_hf_dataset()
            self.assertEqual(len(hf_dataset), 1)
            self.assertEqual(hf_dataset[0]["Transcript"], "Hello World")
            self.assertEqual(hf_dataset[0]["file_path"], json_file_path)

    @patch("level_transcript.storage.Client")
    def test_upload_to_gcp_bucket_labeled(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.upload_from_filename = Mock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Create a temporary file for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.json")
            with open(file_path, "w") as f:
                json.dump({"test": "data"}, f)

            # Use the actual temporary file path in the predictions
            predictions_with_full_path = [(file_path, 2)]  # Simulating a B1 prediction

            # Call the function
            upload_labeled_to_gcp("test_bucket", temp_dir, predictions_with_full_path)

            # Assert the correct GCS blob path and file upload
            mock_bucket.blob.assert_called_once_with("yt_transcripts/B1/test.json")
            mock_blob.upload_from_filename.assert_called_once_with(file_path, content_type="application/json")


    def test_update_json_files_with_labels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.json")
            with open(file_path, "w") as f:
                json.dump({"test": "data"}, f)

            predictions = [(file_path, 0)]  # Simulating an A1 prediction
            update_json_files_with_labels(predictions)

            with open(file_path, "r") as f:
                updated_data = json.load(f)
            self.assertEqual(updated_data["label"], "A1")

    @patch("level_transcript.AutoTokenizer.from_pretrained")
    @patch("level_transcript.AutoModelForSequenceClassification.from_pretrained")
    def test_infer(self, mock_model_class, mock_tokenizer_class):
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            'input_ids': [[101, 102]],
            'attention_mask': [[1, 1]]
        }
        mock_tokenizer_class.return_value = mock_tokenizer

        # Mocking the model and outputs
        mock_model = Mock()
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0]])  # Correct tensor for logits
        mock_model.return_value = mock_outputs
        mock_model.forward.return_value = mock_outputs
        mock_model_class.return_value = mock_model

        dataset = Dataset.from_dict({"Transcript": ["Sample text"], "file_path": ["sample.json"]})

        def mock_map_function(batch):
            return {
                'input_ids': [[101, 102]],
                'attention_mask': [[1, 1]]
            }

        tokenized_dataset = dataset.map(mock_map_function, batched=True)
        predictions = infer(mock_model, tokenized_dataset)
        self.assertEqual(predictions, [("sample.json", 4)])




class TestVideoIdScraper(unittest.TestCase):
    @patch("video_id_scraper.BeautifulSoup")
    def test_get_video_info_valid(self, mock_beautifulsoup):
        div = Mock()
        div.find.return_value = Mock(
            get=Mock(side_effect=lambda x, default=None: "Test Video Title" if x == "title" else "/watch?v=test_video_id")
        )
        expected = {"video_name": "Test Video Title", "video_id": "test_video_id"}
        self.assertEqual(get_video_info(div), expected)

    @patch("video_id_scraper.BeautifulSoup")
    def test_get_video_info_no_title_element(self, mock_beautifulsoup):
        div = Mock()
        div.find.return_value = None  # Simulate missing title element
        self.assertIsNone(get_video_info(div))

    @patch("video_id_scraper.BeautifulSoup")
    def test_get_video_info_invalid_href(self, mock_beautifulsoup):
        div = Mock()
        div.find.return_value = Mock(
            get=Mock(side_effect=lambda x, default=None: "Test Video Title" if x == "title" else "/watch?")
        )
        self.assertIsNone(get_video_info(div))

    @patch("video_id_scraper.webdriver.Chrome")
    @patch("video_id_scraper.BeautifulSoup")
    def test_main(self, mock_beautifulsoup, mock_webdriver):
        def scroll_generator():
            yield 100
            yield 200
            while True:  # Infinite values to simulate no additional scrolling
                yield 200

        mock_driver = MagicMock()
        mock_driver.execute_script.side_effect = scroll_generator()
        mock_webdriver.return_value = mock_driver
        mock_driver.page_source = "<html></html>"

        mock_soup = MagicMock()
        mock_beautifulsoup.return_value = mock_soup
        mock_soup.find_all.return_value = [
            Mock(
                find=Mock(
                    return_value=Mock(
                        get=Mock(side_effect=lambda x, default=None: "Test Video Title" if x == "title" else "/watch?v=test_video_id")
                    )
                )
            )
        ]

        results = main("test_keyword", n_scroll=2)
        mock_driver.get.assert_called_once_with("https://www.youtube.com/results?search_query=test_keyword")
        self.assertEqual(results, [{"video_name": "Test Video Title", "video_id": "test_video_id"}])




if __name__ == "__main__":
    unittest.main()
