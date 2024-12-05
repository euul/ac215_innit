#%%
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, GenerationConfig
from vertexai.batch_prediction import BatchPredictionJob
import json
from google.cloud import storage
# import os

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

#%%
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/text-generator.json"

#%%
# read data from GCP
# Function to read JSON data from GCP bucket and convert it to DataFrame
def read_json_from_gcp(bucket_name, input_file_path, local_file_path):
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    # Get the blob (file)
    blob = bucket.blob(input_file_path)
   # Download the file to the local system
    blob.download_to_filename(local_file_path)

read_json_from_gcp(BUCKET_NAME, INPUT_FILE_PATH, LOCAL_FILE_PATH)
print(f"News article file downloaded to {LOCAL_FILE_PATH}")
#%%
# read data from local
data = []
with open(LOCAL_FILE_PATH, 'r') as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        for line in f:
            data.append(json.loads(line))

# %%
# Include a unique identifier in the input JSONL file
# Because the predictions from GCP batch prediction may not retain the same order as the original input file
data_with_ids = [{"id": idx, **content} for idx, content in enumerate(data)]

# %%
def create_prompt(data):
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

# %%
prompts = [create_prompt(content) for content in data_with_ids]


# %%
system_instruction = (
    "You are a highly skilled language assistant specializing in summarization, CEFR-based vocabulary categorization, and question generation. "
    "When provided with content:\n"
    "1. Generate a summary in under 100 words, and wrap it in <sum> tags.\n"
    "2. Extract key vocabulary from the content, categorized by CEFR levels (A1, A2, B1, B2, C1), and wrap this section in <vocab> tags.\n"
    "   - Present the vocabulary in the format: \{level\}: comma-separated vocabulary.\n"
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

# %%
# Create the JSON structure

output_file = "news_inputs.jsonl"
with open(output_file, "w") as f:
    for prompt in prompts:
        json.dump({
            "request": {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "system_instruction": {
                    "parts": [
                        {
                            "text": system_instruction
                        }
                    ]
                },
                "generationConfig": {
                    "temperature": TEMPERATURE
                }
            }
        }, f)
        f.write("\n")

#%%
# upload to GCP
def upload_to_gcp_bucket(bucket_name, destination_blob_path, source_file_path):
    # Initialize the GCP client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(destination_blob_path)
    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_path}")

upload_to_gcp_bucket(BUCKET_NAME, 'bbc_news/news_inputs.jsonl', 'news_inputs.jsonl')


# %%
INPUT_DATA = "gs://innit_articles_bucket/bbc_news/news_inputs.jsonl"

# %%
# Initialize Vertex AI client
vertexai.init(project=PROJECT_ID, location=REGION)

model = GenerativeModel(model_name=MODEL_ID)

# %%
job = BatchPredictionJob.submit(
    source_model=MODEL_ID, input_dataset=INPUT_DATA, output_uri_prefix=OUTPUT_URL
)
# # %%
# print(f"Job resource name: {job.resource_name}")
# print(f"Model resource name: {job.model_name}")
# print(f"Job state: {job.state.name}")


# %%

# # Take a look at the output
# file_path = "bbc_news_prediction-model-2024-11-25T15_32_07.034415Z_predictions.jsonl"

# # Read and parse the file
# pred = []
# with open(file_path, 'r', encoding='utf-8') as file:
#     for line in file:
#         pred.append(json.loads(line))

# print(pred[0]['response']['candidates'][0]['content']['parts'][0]['text'])
# # %%
