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

#%%
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
    for line in f:
        data.append(json.loads(line))


# %%
def create_prompt(data):
    content = data["Text"]
    prompt = (
        f"Please summarize the following content in under 100 words, wrapping the summary in <sum> tags. After the summary, extract key vocabulary from the content, categorizing it by CEFR levels (A1, A2, B1, B2, C1), and wrap the vocabulary section in <vocab> tags. Each category should include words and short phrases representative of that level. \n"
        "Present the vocabulary in the following format: \{level\}: comma-separated vocabulary"
        "The vocabulary should be words only and not phrases."
        "For example: \n"
        '''    
        <vocab>
        A1: war, money, people, office  
        A2: missiles, attacks, support, decision, promise, end, change  
        B1: administration, policy, involvement, mandate, allies, condemn, escalate, efforts, critical, approach, weapons, conflict  
        B2: consternation, long-standing, significant, incoming, authorisation, deployment, retribution, magnitude, anticipated, emphasizing  
        C1: escalation, slow-walked, doctrine, sanctuary
        </vocab>
        '''
        "\n\nHere is the content: \n"
        f"{content}"
    )
    return prompt
# %%
prompts = [create_prompt(content) for content in data]

# %%
system_instruction=(
    "You are a highly skilled language assistant specializing in summarization and CEFR-based vocabulary categorization. When given a content:"
    "1. Generate a summary in under 100 words, and wrap it in <sum> tags."
    "2. Extract key vocabulary and categorize it by CEFR levels (A1, A2, B1, B2, C1), wrapping this section in <vocab> tags."
    "Present the vocabulary in the format: \{level\}: comma-separated vocabulary/phrases."
    "Ensure each level contains appropriate vocabulary with words representative of that level."
    "The vocabulary should be words only and not phrases."
    "Maintain clarity and organization in the output."
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
