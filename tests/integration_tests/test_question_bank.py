import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import json
import os
import sys

# Ensure /app is in the Python path
sys.path.insert(0, '/app')

import generate_test
import upload_questions

# Set a default value for the --level argument
sys.argv.extend(["--level", "A1"])

class TestQuestionBank(unittest.TestCase):

    @patch("generate_test.vertexai.init")
    @patch("generate_test.GenerativeModel")
    def test_generate_test(self, mock_generative_model, mock_vertexai_init):
        # Mock responses
        mock_chat_session = MagicMock()
        mock_generative_model.return_value.start_chat.return_value = mock_chat_session
        mock_chat_session.send_message.return_value.text = """
        [
            {
                "question": "Sample Question?",
                "choices": ["A", "B", "C"],
                "correct_answer": "A",
                "level": "A1"
            }
        ]
        """

        # Mock the input JSON file with at least 5 items
        example_data = [
            {"question": f"Example {i}?", "choices": ["A", "B", "C"], "correct_answer": "B", "level": "A1"}
            for i in range(5)
        ]
        mocked_open = mock_open(read_data=json.dumps(example_data))

        # Handle both read and write operations with side_effect
        def open_side_effect(file, mode="r", *args, **kwargs):
            if mode == "r" and file == "combined_questions.json":
                return mocked_open(file, mode, *args, **kwargs)
            elif mode == "w" and file.startswith("./generated_questions/"):
                return mocked_open(file, mode, *args, **kwargs)
            raise FileNotFoundError(f"Unexpected file or mode: {file}, {mode}")

        with patch("builtins.open", side_effect=open_side_effect) as mock_file:
            with patch("os.makedirs") as mock_makedirs:
                # Mock sys.argv to pass the required --level argument
                with patch("sys.argv", ["generate_test.py", "--level", "A1"]):
                    generate_test.main()

                # Assertions
                mock_vertexai_init.assert_called_once_with(
                    project=generate_test.PROJECT_ID, location=generate_test.REGION
                )
                mock_generative_model.assert_called_once_with(
                    model_name=generate_test.MODEL_ID,
                    system_instruction=unittest.mock.ANY
                )
                mock_chat_session.send_message.assert_called()

                # Ensure both read and write operations were called
                mock_file.assert_any_call("combined_questions.json", "r")
                mock_file.assert_any_call("./generated_questions/generated_questions_A1.json", "w")
                mock_makedirs.assert_called_once_with(generate_test.OUTPUT_DIR, exist_ok=True)

    @patch("upload_questions.storage.Client")  # Mock the GCP Storage Client
    def test_upload_questions(self, mock_storage_client):
        # Mock GCP bucket and blob behavior
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock local files
        with patch("os.listdir") as mock_listdir:
            mock_listdir.return_value = ["generated_questions_A1.json", "generated_questions_A2.json"]

            # Call the upload_questions script
            upload_questions.main()

            # Assertions
            mock_storage_client.assert_called_once_with(project=upload_questions.PROJECT_ID)
            mock_bucket.blob.assert_any_call("generated_questions/generated_questions_A1.json")
            mock_bucket.blob.assert_any_call("generated_questions/generated_questions_A2.json")
            mock_blob.upload_from_filename.assert_any_call("./generated_questions/generated_questions_A1.json")
            mock_blob.upload_from_filename.assert_any_call("./generated_questions/generated_questions_A2.json")


    @patch("subprocess.run")
    def test_cli(self, mock_subprocess_run):
        # Call the cli script
        import cli
        cli.main()

        # Assertions
        mock_subprocess_run.assert_has_calls([
            call(["python", "generate_test.py", "--level", "A1"]),
            call(["python", "generate_test.py", "--level", "A2"]),
            call(["python", "generate_test.py", "--level", "B1"]),
            call(["python", "generate_test.py", "--level", "B2"]),
            call(["python", "generate_test.py", "--level", "C1"]),
            call(["python", "upload_questions.py"])
        ])

if __name__ == "__main__":
    unittest.main()
