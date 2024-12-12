#%%
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, GenerationConfig
from vertexai.batch_prediction import BatchPredictionJob
import json
from google.cloud import storage
import os

# Configuration
TEMPERATURE = 0.5
PROJECT_ID = "innit-437518"
REGION = 'us-central1'
MODEL_ID = 'gemini-1.5-pro-002'

BUCKET_NAME = "innit_articles_bucket"
MODULE_BLOB_NAME = "yt_transcripts"
LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']

N_QUESTIONS = 5

#%%
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/text-generator.json"
#%%
# read data from GCP
# Function to read JSON data from GCP bucket and convert it to DataFrame

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



# %%
def create_prompt(content, id):
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



def main(): # pragma: no cover

    read_json_from_gcp()# %%
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
                if file_name.endswith(".json") and file_name != "id_mapping.json":  # Check if the file is a JSON file
                    file_path = os.path.join(local_file_path, file_name) 
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        # print(data.keys())
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

if __name__ == "__main__":
    main() # pragma: no cover


