import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, ChatSession, GenerationConfig
import argparse
import os
from datasets import Dataset, load_from_disk
import json
import time
import random

# Setup the arguments for the trainer task
parser = argparse.ArgumentParser()
parser.add_argument(
    "--level", dest="level", required=True, type=str, choices=["A1", "A2", "B1", "B2", "C1"], help="Target level for the generated text"
)
# TBC
parser.add_argument("--n_samples", dest="n_samples", default=10, type=int, help="Number of samples to generate")
args = parser.parse_args()

# Local directory to read the train dataset
LOCAL_DATASET_DIR = './datasets'
# Output file path of the generated text and corresponding prompt
OUTPUT_FILE_PATH = "output-" + args.level +".json"

# Number of examples for few-shot learning
N_EXAMPLES = 5 
# Maximum length of the generated text
MAX_OUTPUT_TOKENS = 1000
# Temperature for sampling from the model
TEMPERATURE = 0.5

# Project and model information
PROJECT_ID = "innit-437518"
REGION = 'us-central1'
MODEL_ID = 'gemini-1.5-flash-002'


LEVEL_LABEL_MAPPING = {'A1': 0,
                        'A2': 1,
                        'B1': 2,
                        'B2': 3,
                        'C1': 4}

# # TBC: Load Google service account credentials
# credentials = service_account.Credentials.from_service_account_file(
#     "/Users/pc/Documents/Harvard_DS/24fall/AC_215_Advanced_Practical_Data_Science/Project/secrets/text-generator.json"
# )

# export GOOGLE_APPLICATION_CREDENTIALS="/Users/pc/Documents/Harvard_DS/24fall/AC_215_Advanced_Practical_Data_Science/Project/secrets/text-generator.json"

# Load train dataset
def load_datasets(local_dataset_dir):
    """Load datasets from the local disk."""
    train_dataset_path = os.path.join(local_dataset_dir, 'train_dataset')
    
    # Check if the directory exists
    if os.path.exists(train_dataset_path):
        train_dataset = load_from_disk(train_dataset_path)
        print("Successfully loaded datasets from disk")
        return train_dataset
    else:
        raise FileNotFoundError(
            f"Train dataset does not exist at '{train_dataset_path}'. Please run download_train_datasets.py first to download the data."
        )

train_dataset = load_datasets(LOCAL_DATASET_DIR)


# Get label
label = LEVEL_LABEL_MAPPING[args.level]

# Get samples for the given label
label_subset = train_dataset.filter(lambda example: example['label'] == label)
random_samples = label_subset.shuffle(seed=42).select(range(N_EXAMPLES))
transcripts = random_samples['Transcript']  # Extract transcripts

# Few-shot prompt setup
system_instruction = (
    f"Generate English learning material (a transcript of video or audio) suitable for {args.level}-level learners. "
    "Ensure the material is comparable in difficulty to the provided examples. "
    "If the transcript is a dialogue, it should not contain additional contextual phrases or commentary. "
    "Please wrap the transcript using <Transcript> tags."
)

# prompt = ""
# for i, example in enumerate(transcripts, start=1):
#     prompt += f"Example {i}:\n{example}\n\n"


# Initialize the Vertex AI client
vertexai.init(project=PROJECT_ID, location=REGION)

model = GenerativeModel(
    model_name=MODEL_ID,
    system_instruction = system_instruction
    )


generation_config = GenerationConfig(temperature=TEMPERATURE, max_output_tokens=MAX_OUTPUT_TOKENS)

chat_session = model.start_chat()

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    response = chat.send_message(prompt, 
                                  generation_config=generation_config)
    return response.text

output_data = []

for _ in range(args.n_samples):
    # Shuffle and select new examples for each prompt
    shuffled_subset = label_subset.shuffle(seed=42 + _)  # Change seed to get different samples
    random_samples = shuffled_subset.select(range(N_EXAMPLES))
    transcripts = random_samples['Transcript']
    
    # Generate a new prompt with updated examples
    prompt = ""
    for i, example in enumerate(transcripts, start=1):
        prompt += f"Example {i}:\n{example}\n\n"
    
    # Get the response
    response = get_chat_response(chat_session, prompt)
    
    # Append the prompt and response to the output data
    output_data.append({
        "prompt": prompt,
        "response": response
    })

    time.sleep(random.uniform(0, 2))

with open(OUTPUT_FILE_PATH, "w") as f:
    json.dump(output_data, f, indent=4)


