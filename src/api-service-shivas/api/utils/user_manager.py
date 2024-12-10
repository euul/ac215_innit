import bcrypt
import json
import os
from google.cloud import storage
from datetime import datetime, timedelta
import jwt
import logging

logging.basicConfig(level=logging.INFO)

class UserManager:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._storage_client = None  # Lazy initialization for storage.Client
        self.jwt_secret = os.getenv("JWT_SECRET", "your_jwt_secret")
        self.jwt_algorithm = "HS256"

    @property
    def storage_client(self):
        """Initialize storage.Client lazily."""
        if self._storage_client is None:
            self._storage_client = storage.Client()
        return self._storage_client

    def _get_bucket(self):
        try:
            return self.storage_client.bucket(self.bucket_name)
        except Exception as e:
            raise Exception(f"Error accessing bucket: {str(e)}")

    def _get_user_blob(self, username):
        """Get the GCP blob for a user."""
        bucket = self._get_bucket()
        return bucket.blob(f"users/{username}.json")

    def register_user(self, username: str, password: str, metadata: dict):
        """Register a new user."""
        if not username or not password:
            raise Exception("Username and password are required")
        if len(password) < 8:
            raise Exception("Password must be at least 8 characters long")

        blob = self._get_user_blob(username)
        if blob.exists():
            raise Exception(f"Username '{username}' already exists")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        valid_metadata = {key: str(value) for key, value in metadata.items()}

        user_data = {
            "username": username,
            "password": hashed_password.decode("utf-8"),
            "metadata": valid_metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            blob.upload_from_string(json.dumps(user_data), content_type="application/json")
            logging.info(f"User '{username}' registered successfully")
        except Exception as e:
            logging.error(f"Error saving user data for '{username}': {str(e)}")
            raise Exception("Error saving user data")

    def authenticate_user(self, username: str, password: str):
        """Authenticate a user."""
        try:
            # Fetch user data
            print(f"Attempting login for username: {username}")
            blob = self._get_user_blob(username)
            if not blob.exists():
                print(f"Authentication failed for '{username}': User not found")
                raise Exception("Invalid username or password")

            user_data = json.loads(blob.download_as_text())
            hashed_password = user_data.get("password")

            # Verify password
            if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
                logging.warning(f"Authentication failed for '{username}': Incorrect password")
                raise Exception("Invalid username or password")

            # Generate JWT token
            token_payload = {
                "username": username,
                "exp": datetime.utcnow() + timedelta(hours=1)  # Set token expiration
            }
            token = jwt.encode(token_payload, self.jwt_secret, algorithm=self.jwt_algorithm)

            print(f"User '{username}' authenticated successfully")
            return token
        except Exception as e:
            print(f"Authentication error for '{username}': {str(e)}")
            raise Exception("Authentication failed")

    def update_metadata(self, username: str, metadata: dict):
        blob = self._get_user_blob(username)
        if not blob.exists():
            raise Exception(f"User '{username}' not found")

        user_data = json.loads(blob.download_as_text())
        user_data["metadata"].update(metadata)  # Merge new metadata

        try:
            blob.upload_from_string(json.dumps(user_data), content_type="application/json")
        except Exception as e:
            raise Exception(f"Error updating metadata for '{username}': {str(e)}")
        
    def get_metadata(self, username: str) -> dict:
        """
        Retrieve the metadata for a user.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            dict: The metadata for the user or an empty dictionary if not found.
        """
        blob = self._get_user_blob(username)
        if not blob.exists():
            raise Exception(f"User '{username}' not found")

        user_data = json.loads(blob.download_as_text())
        return user_data.get("metadata", {})


