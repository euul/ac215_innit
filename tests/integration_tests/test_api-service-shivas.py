import unittest
from fastapi.testclient import TestClient
import sys
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
import bcrypt
import jwt
import json

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

from api.routers.diagnostic import router as router_diagnostic
from api.utils.media_manager import MediaManager
from api.utils.user_manager import UserManager


class TestDiagnosticAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up the test client for the FastAPI router."""
        self.client = TestClient(router_diagnostic)

    @patch('api.routers.diagnostic.storage.Client')  # Mock the GCP Storage Client
    def test_get_diagnostic_test_success(self, mock_storage_client):
        """Test fetching the diagnostic test successfully."""
        # Mock the GCP client, bucket, and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock blob behavior
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps([
            {"question": "What is 2 + 2?", "choices": ["3", "4", "5"], "answer": "4"},
            {"question": "What is the capital of France?", "choices": ["Berlin", "Madrid", "Paris"], "answer": "Paris"}
        ])

        # Call the API
        response = self.client.get("/diagnostic")

        # Assert API response
        self.assertEqual(response.status_code, 200)
        self.assertIn("questions", response.json())
        self.assertEqual(len(response.json()["questions"]), 2)

class TestMediaManager(unittest.TestCase):

    def setUp(self):
        """Set up the MediaManager instance for testing."""
        self.media_manager = MediaManager(bucket_name="test_bucket")

    @patch("api.utils.media_manager.storage.Client")
    def test_fetch_json_files_from_gcp_success(self, mock_storage_client):
        """Test fetching JSON files successfully from GCP."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [
            MagicMock(name="folder/file1.json"),
            MagicMock(name="folder/file2.json"),
        ]

        # Mock blob content
        mock_blob.download_as_text.side_effect = [
            '{"id": 1, "content": "Test content 1"}',
            '{"id": 2, "content": "Test content 2"}'
        ]
        mock_bucket.list_blobs.return_value = [mock_blob, mock_blob]

        data = self.media_manager._fetch_json_files_from_gcp("folder")

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[1]["id"], 2)

    @patch("api.utils.media_manager.storage.Client")
    def test_fetch_json_files_from_gcp_no_json(self, mock_storage_client):
        """Test fetching JSON files with no JSON files in the folder."""
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [MagicMock(name="folder/file1.txt")]

        data = self.media_manager._fetch_json_files_from_gcp("folder")

        self.assertEqual(len(data), 0)

    @patch("api.utils.media_manager.MediaManager._fetch_json_files_from_gcp")
    def test_get_video_transcripts(self, mock_fetch_json):
        """Test fetching video transcripts by level."""
        mock_fetch_json.return_value = [
            {"video_id": "1", "content": "Video 1 content"},
            {"video_id": "2", "content": "Video 2 content"}
        ]

        transcripts = self.media_manager.get_video_transcripts(level='A1')

        mock_fetch_json.assert_called_once_with("yt_transcripts/A1/")
        self.assertEqual(len(transcripts), 2)
        self.assertEqual(transcripts[0]["video_id"], "1")

    @patch("api.utils.media_manager.MediaManager._fetch_json_files_from_gcp")
    def test_get_articles(self, mock_fetch_json):
        """Test fetching articles by level."""
        mock_fetch_json.return_value = [
            {"id": "1", "content": "Article 1 content"},
            {"id": "2", "content": "Article 2 content"}
        ]

        articles = self.media_manager.get_articles(level="B1")

        mock_fetch_json.assert_called_once_with("bbc_news/B1/")
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["id"], "1")

    @patch("api.utils.media_manager.MediaManager.get_articles")
    def test_get_article_by_id_found(self, mock_get_articles):
        """Test fetching a specific article by ID successfully."""
        mock_get_articles.return_value = [
            {"id": "1", "content": "Article 1 content"},
            {"id": "2", "content": "Article 2 content"}
        ]

        article = self.media_manager.get_article_by_id(article_id="2", level="B2")

        mock_get_articles.assert_called_once_with("B2")
        self.assertIsNotNone(article)
        self.assertEqual(article["id"], "2")

    @patch("api.utils.media_manager.MediaManager.get_articles")
    def test_get_article_by_id_not_found(self, mock_get_articles):
        """Test fetching a specific article by ID that does not exist."""
        mock_get_articles.return_value = [
            {"id": "1", "content": "Article 1 content"}
        ]

        article = self.media_manager.get_article_by_id(article_id="3", level="B2")

        mock_get_articles.assert_called_once_with("B2")
        self.assertIsNone(article)

    @patch("api.utils.media_manager.MediaManager.get_video_transcripts")
    def test_get_video_by_id_found(self, mock_get_transcripts):
        """Test fetching a specific video by ID successfully."""
        mock_get_transcripts.return_value = [
            {"video_id": "1", "content": "Video 1 content"},
            {"video_id": "2", "content": "Video 2 content"}
        ]

        video = self.media_manager.get_video_by_id(video_id="2", level="A1")

        mock_get_transcripts.assert_called_once_with("A1")
        self.assertIsNotNone(video)
        self.assertEqual(video["video_id"], "2")

    @patch("api.utils.media_manager.MediaManager.get_video_transcripts")
    def test_get_video_by_id_not_found(self, mock_get_transcripts):
        """Test fetching a specific video by ID that does not exist."""
        mock_get_transcripts.return_value = [
            {"video_id": "1", "content": "Video 1 content"}
        ]

        video = self.media_manager.get_video_by_id(video_id="3", level="A1")

        mock_get_transcripts.assert_called_once_with("A1")
        self.assertIsNone(video)


class TestUserManager(unittest.TestCase):
    def setUp(self):
        """Set up UserManager instance and test data."""
        self.user_manager = UserManager(bucket_name="test_bucket")
        self.username = "test_user"
        self.password = "securepassword"
        self.metadata = {"level": "B2"}
        self.hashed_password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        self.jwt_secret = self.user_manager.jwt_secret
        self.jwt_algorithm = self.user_manager.jwt_algorithm

    @patch("api.utils.user_manager.storage.Client")
    def test_register_user_success(self, mock_storage_client):
        """Test registering a user successfully."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = False

        self.user_manager.register_user(self.username, self.password, self.metadata)

        mock_blob.upload_from_string.assert_called_once()
        uploaded_data = json.loads(mock_blob.upload_from_string.call_args[0][0])
        self.assertEqual(uploaded_data["username"], self.username)
        self.assertIn("password", uploaded_data)
        self.assertEqual(uploaded_data["metadata"], self.metadata)

    @patch("api.utils.user_manager.storage.Client")
    def test_register_user_already_exists(self, mock_storage_client):
        """Test registering a user that already exists."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True

        with self.assertRaises(Exception) as context:
            self.user_manager.register_user(self.username, self.password, self.metadata)

        self.assertEqual(str(context.exception), f"Username '{self.username}' already exists")

    @patch("api.utils.user_manager.storage.Client")
    def test_authenticate_user_success(self, mock_storage_client):
        """Test authenticating a user successfully."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps({
            "username": self.username,
            "password": self.hashed_password,
            "metadata": self.metadata,
        })

        token = self.user_manager.authenticate_user(self.username, self.password)

        decoded_token = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        self.assertEqual(decoded_token["username"], self.username)

    @patch("api.utils.user_manager.storage.Client")
    def test_authenticate_user_invalid_credentials(self, mock_storage_client):
        """Test authenticating a user with invalid credentials."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps({
            "username": self.username,
            "password": self.hashed_password,
            "metadata": self.metadata,
        })

        with self.assertRaises(Exception) as context:
            self.user_manager.authenticate_user(self.username, "wrongpassword")

        self.assertEqual(str(context.exception), "Authentication failed")

    @patch("api.utils.user_manager.storage.Client")
    def test_update_metadata_success(self, mock_storage_client):
        """Test updating metadata for a user successfully."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps({
            "username": self.username,
            "password": self.hashed_password,
            "metadata": self.metadata,
        })

        updated_metadata = {"new_key": "new_value"}
        self.user_manager.update_metadata(self.username, updated_metadata)

        mock_blob.upload_from_string.assert_called_once()
        updated_data = json.loads(mock_blob.upload_from_string.call_args[0][0])
        self.assertEqual(updated_data["metadata"]["new_key"], "new_value")

    @patch("api.utils.user_manager.storage.Client")
    def test_get_metadata_success(self, mock_storage_client):
        """Test retrieving metadata for a user successfully."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json.dumps({
            "username": self.username,
            "password": self.hashed_password,
            "metadata": self.metadata,
        })

        retrieved_metadata = self.user_manager.get_metadata(self.username)
        self.assertEqual(retrieved_metadata, self.metadata)

    @patch("api.utils.user_manager.storage.Client")
    def test_get_metadata_user_not_found(self, mock_storage_client):
        """Test retrieving metadata for a non-existent user."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = False

        with self.assertRaises(Exception) as context:
            self.user_manager.get_metadata(self.username)

        self.assertEqual(str(context.exception), f"User '{self.username}' not found")


if __name__ == "__main__":
    unittest.main()
