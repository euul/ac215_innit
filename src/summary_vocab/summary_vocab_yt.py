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
MODULE_BLOB_NAME = "yt_transcripts"
LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']

# OUTPUT_URL = "gs://innit_articles_bucket/yt_transcripts"

#%%
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/text-generator.json"

#%%
# read data from GCP
# Function to read JSON data from GCP bucket and convert it to DataFrame
import os
from google.cloud import storage

def read_json_from_gcp():
    # Initialize the GCP client
    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for level in LEVELS:
        prefix = MODULE_BLOB_NAME + '/' + level
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        for blob in blobs:
            if blob.name.endswith(".json"):
                # Ensure that the directory structure exists locally
                local_dir = os.path.dirname(blob.name)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)  # Create the directory if it doesn't exist

                # Download the file to the local system
                blob.download_to_filename(blob.name)

        print(f"Files downloaded to {prefix}")

read_json_from_gcp()

# %%
def create_prompt(content, id):
    prompt = (
        f"ID: {id}\n"
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
system_instruction=(
    "You are a highly skilled language assistant specializing in summarization and CEFR-based vocabulary categorization. When given a content:"
    "1. Generate a summary in under 100 words, and wrap it in <sum> tags."
    "2. Extract key vocabulary and categorize it by CEFR levels (A1, A2, B1, B2, C1), wrapping this section in <vocab> tags."
    "Present the vocabulary in the format: \{level\}: comma-separated vocabulary/phrases."
    "Ensure each level contains appropriate vocabulary with words representative of that level."
    "The vocabulary should be words only and not phrases."
    "Maintain clarity and organization in the output."
)

#%%
# create prompts inputs for each level folder
for level in LEVELS:
    local_file_path = f'yt_transcripts/{level}'
    output_file = f"yt_transcripts/{level}/inputs.jsonl"
    id_mapping_file = f"yt_transcripts/{level}/id_mapping.json"

    if os.path.exists(local_file_path):
        prompts = []
        id_mapping = {}
        id_counter = 1

        for file_name in os.listdir(local_file_path):
            if file_name.endswith(".json"):  # Check if the file is a JSON file
                file_path = os.path.join(local_file_path, file_name) 
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    concatenated_text = ' '.join([entry['text'] for entry in data['transcript']])
                    prompts.append(create_prompt(concatenated_text, id_counter))
                    id_mapping[id_counter] = file_name
                    id_counter += 1
        
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

        # Save ID to file name mapping
        with open(id_mapping_file, "w") as mapping_file:
            json.dump(id_mapping, mapping_file, indent=4)
        print(f"ID mapping file created for {level}")

        # upload to GCP
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{MODULE_BLOB_NAME}/{level}/inputs.jsonl")
        blob.upload_from_filename(output_file)
        print(f"File {output_file} uploaded to gs://{BUCKET_NAME}/{MODULE_BLOB_NAME}/{level}/inputs.jsonl")
        blob = bucket.blob(f"{MODULE_BLOB_NAME}/{level}/id_mapping.json")
        blob.upload_from_filename(id_mapping_file)
        print(f"File {id_mapping_file} uploaded to gs://{BUCKET_NAME}/{MODULE_BLOB_NAME}/{level}/id_mapping.json")


# %%
# batch prediction
for level in LEVELS:
    INPUT_DATA = f"gs://innit_articles_bucket/{MODULE_BLOB_NAME}/{level}/inputs.jsonl"
    OUTPUT_URL = f"gs://innit_articles_bucket/{MODULE_BLOB_NAME}/{level}"

    # Check if the input JSON file exists in GCS
    input_blob_path = f"{MODULE_BLOB_NAME}/{level}/inputs.jsonl"

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(input_blob_path)
        if blob.exists():
            # Initialize Vertex AI client
            vertexai.init(project=PROJECT_ID, location=REGION)

            model = GenerativeModel(model_name=MODEL_ID)

            # Submit the batch prediction job
            job = BatchPredictionJob.submit(
                source_model=MODEL_ID, input_dataset=INPUT_DATA, output_uri_prefix=OUTPUT_URL
            )

            print(f"Batch prediction job submitted for level {level}")
            print(f"Job resource name: {job.resource_name}")
            print(f"Model resource name: {job.model_name}")
            print(f"Job state: {job.state.name}")
        else:
            print(f"No input file found for level {level}. Skipping batch prediction.")
    except Exception as e:
        print(f"Error checking or processing level {level}: {e}")



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
