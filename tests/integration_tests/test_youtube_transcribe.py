import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
import json
import shutil
from google.cloud import storage
from get_transcript import (
    get_transcript,
    clean_timestamps,
    upload_to_gcp_bucket,
    save_transcripts,
    cleanup_local_folder,
    main as get_transcript_main
)
from video_id_scraper import (
    get_video_info,
    main as video_id_scraper_main
)

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
    def test_upload_to_gcp_bucket(self, mock_storage_client):
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        local_folder = tempfile.mkdtemp()
        file_path = os.path.join(local_folder, "test.json")
        with open(file_path, "w") as f:
            json.dump({"test": "data"}, f)

        upload_to_gcp_bucket("test_bucket", "test_folder", local_folder)
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

    @patch("video_id_scraper.webdriver.Chrome")
    @patch("video_id_scraper.BeautifulSoup")
    def test_video_id_scraper_main(self, mock_beautifulsoup, mock_webdriver):
        def scroll_generator():
            yield 100
            yield 200
            while True:
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

        results = video_id_scraper_main("test_keyword", n_scroll=2)
        mock_driver.get.assert_called_once_with("https://www.youtube.com/results?search_query=test_keyword")
        self.assertEqual(results, [{"video_name": "Test Video Title", "video_id": "test_video_id"}])

if __name__ == "__main__":
    unittest.main()
