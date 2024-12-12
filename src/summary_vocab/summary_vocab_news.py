import json
import vertexai
from google.cloud import storage
from vertexai.preview.generative_models import GenerativeModel, ChatSession, GenerationConfig
from vertexai.batch_prediction import BatchPredictionJob
import time

# Configuration
TEMPERATURE = 0.5
PROJECT_ID = "innit-437518"
REGION = 'us-central1'
MODEL_ID = 'gemini-1.5-pro-002'
BUCKET_NAME = "innit_articles_bucket"
INPUT_FILE_PATH = "bbc_news/bbc_news_articles_labeled.json"
LOCAL_FILE_PATH = "bbc_news_articles_labeled.json"
OUTPUT_URL = "gs://innit_articles_bucket/bbc_news"
N_QUESTIONS = 5

# GCP File Handling
def read_json_from_gcp(bucket_name, input_file_path, local_file_path):
    """Read JSON data from GCP bucket and save to local file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(input_file_path)
    blob.download_to_filename(local_file_path)
    print(f"News article file downloaded to {local_file_path}")

def load_local_data(local_file_path):
    """Load JSON data from local file."""
    data = []
    with open(local_file_path, 'r') as f:
        try:
            for line in f:
                data.append(json.loads(line))
        except json.JSONDecodeError:
            data = json.load(f)
    return data

# Data Processing
def add_unique_ids_to_data(data):
    """Add unique ID to each item in the data."""
    return [{"id": idx, **content} for idx, content in enumerate(data)]

def create_prompt(data):
    """Generate the prompt for the model based on the article content."""
    content = data["Text"]
    id = data["id"]
    prompt = (
        f"ID: {id}\n"
        f"Please summarize the following content in under 100 words, wrapping the summary in `<sum>` tags. "
        f"After the summary, extract key vocabulary from the content, categorized by CEFR levels (A1, A2, B1, B2, C1), and wrap the vocabulary section in `<vocab>` tags. "
        "Each category should include a comma-separated list of words representative of that level, with no phrases or multi-word terms. "
        "Format the vocabulary as follows:\n"
        "<vocab>\n"
        "A1: word1, word2, word3\n"
        "A2: word1, word2, word3\n"
        "B1: word1, word2, word3\n"
        "B2: word1, word2, word3\n"
        "C1: word1, word2, word3\n"
        "</vocab>\n"
        "\nAfter the vocabulary, generate exactly {N_QUESTIONS} questions related to the content, wrapping the questions in `<questions>` tags. "
        "Each question should include:\n"
        "- The question text\n"
        "- Three answer choices (A, B, C)\n"
        "- The correct answer (e.g., \"A\")\n"
        "- The CEFR level (A1, A2, B1, B2, C1)\n"
        "\nFormat the questions as a JSON array following this structure:\n"
        "<questions>\n"
        "[\n"
        "    {\n"
        '        "question": "Question text?",\n'
        '        "choices": ["A", "B", "C"],\n'
        '        "answer": "A",\n'
        '        "level": "A1"\n'
        "    },\n"
        "    {\n"
        '        "question": "Question text?",\n'
        '        "choices": ["A", "B", "C"],\n'
        '        "answer": "B",\n'
        '        "level": "B1"\n'
        "    }\n"
        "]\n"
        "</questions>\n"
        "\nHere is the content:\n"
        f"{content}"
    )
    return prompt

def generate_prompts(data_with_ids):
    """Generate prompts for each article in the dataset."""
    return [create_prompt(content) for content in data_with_ids]

# System Instructions
system_instruction = (
    "You are a highly skilled language assistant specializing in summarization, CEFR-based vocabulary categorization, and question generation. "
    "When provided with content:\n"
    "1. Generate a summary in under 100 words, and wrap it in <sum> tags.\n"
    "2. Extract key vocabulary from the content, categorized by CEFR levels (A1, A2, B1, B2, C1), and wrap this section in <vocab> tags.\n"
    "   - Present the vocabulary in the format: {level}: comma-separated vocabulary.\n"
    "   - Ensure each level contains appropriate vocabulary with words representative of that level.\n"
    "   - The vocabulary should consist of single words only (no phrases or multi-word terms).\n"
    "3. Generate a specified number of questions (e.g., 5) based on the content, wrapping them in <questions> tags.\n"
    "   - Each question should include:\n"
    "     - The question text\n"
    "     - Three answer choices (A, B, C)\n"
    "     - The correct answer (e.g., \"A\")\n"
    "     - The CEFR level (A1, A2, B1, B2, C1)\n"
    "   - Format the questions as a JSON array, following this structure:\n"
    '     <questions>\n'
    '     [\n'
    '         {\n'
    '             "question": "Sample question?",\n'
    '             "choices": ["Option A", "Option B", "Option C"],\n'
    '             "answer": "A",\n'
    '             "level": "A1"\n'
    '         },\n'
    '         {\n'
    '             "question": "Another sample question?",\n'
    '             "choices": ["Option A", "Option B", "Option C"],\n'
    '             "answer": "B",\n'
    '             "level": "B1"\n'
    '         }\n'
    '     ]\n'
    '     </questions>\n'
    "Ensure all output is clear, structured, and accurately formatted as requested."
)

# File Handling
def save_prompts_to_jsonl(prompts, output_file="news_inputs.jsonl"):
    """Save prompts to a JSONL file."""
    with open(output_file, "w") as f:
        for prompt in prompts:
            json.dump({
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "system_instruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "generationConfig": {
                        "temperature": TEMPERATURE
                    }
                }
            }, f)
            f.write("\n")
    print(f"Prompts saved to {output_file}")

def upload_to_gcp(bucket_name, destination_blob_path, source_file_path):
    """Upload a file to a GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_path)
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_path}")

# Batch Prediction
def submit_batch_prediction(input_data, output_url):
    """Submit a batch prediction job."""
    vertexai.init(project=PROJECT_ID, location=REGION)
    model = GenerativeModel(model_name=MODEL_ID)
    job = BatchPredictionJob.submit(
        source_model=MODEL_ID, input_dataset=input_data, output_uri_prefix=output_url
    )
    return job

# Main Execution Flow
def main():  # pragma: no cover
    # Read data from GCP and load locally
    read_json_from_gcp(BUCKET_NAME, INPUT_FILE_PATH, LOCAL_FILE_PATH)
    data = load_local_data(LOCAL_FILE_PATH)

    print(data)
    # Add unique IDs and generate prompts
    data_with_ids = add_unique_ids_to_data(data)
    # print(data_with_ids[0])

    prompts = generate_prompts(data_with_ids)

    # Save prompts to JSONL and upload to GCP
    save_prompts_to_jsonl(prompts)
    print("Prompts saved to JSONL file")
    upload_to_gcp(BUCKET_NAME, 'bbc_news/news_inputs.jsonl', 'news_inputs.jsonl')

    # Submit batch prediction
    input_data = "gs://innit_articles_bucket/bbc_news/news_inputs.jsonl"
    job = submit_batch_prediction(input_data, OUTPUT_URL)
    print(f"Batch prediction job submitted: {job.resource_name}")

    # Check job status
    print(f"Job resource name: {job.resource_name}")
    print(f"Model resource name with the job: {job.model_name}")
    print(f"Job state: {job.state.name}")

    # Refresh the job until complete
    while not job.has_ended:
        time.sleep(10)
        job.refresh()

    # Check if the job succeeds
    if job.has_succeeded:
        print("Job succeeded!")
    else:
        print(f"Job failed: {job.error}")

if __name__ == "__main__":
    main() # pragma: no cover
