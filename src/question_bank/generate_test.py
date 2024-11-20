import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, GenerationConfig
import json
import random
import os
import argparse
# Configuration
TEMPERATURE = 0.5
PROJECT_ID = "innit-437518"
REGION = 'us-central1'
MODEL_ID = 'gemini-1.5-pro-002'
N_QUESTIONS = 10
N_LOOPS = 5
EXAMPLE_FILE_PATH = "combined_questions.json"
OUTPUT_DIR = "./generated_questions/"  # Directory to save the output

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--level", required=True, type=str, choices=["A1", "A2", "B1", "B2", "C1"],
        help="Target level for the generated text"
    )
    return parser.parse_args()


def main():  # pragma: no cover
    args = parse_arguments()

    OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, f"generated_questions_{args.level}.json")

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the JSON file
    with open(EXAMPLE_FILE_PATH, "r") as file:
        data = json.load(file)

    # Filter examples with "level": args.level
    examples = [item for item in data if item.get("level") == args.level]

    # Initialize Vertex AI client
    # vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)
    vertexai.init(project=PROJECT_ID, location=REGION)

    model = GenerativeModel(
        model_name=MODEL_ID,
        system_instruction=(
            "You are an English teacher specializing in compiling placement test banks. "
            "Your task is to generate exactly {N_QUESTIONS} test questions for an {args.level}-level English test. "
            "Each question should include: a question text, three answer choices (A, B, C), the correct answer, and the level. "
            "Ensure the output is in JSON format and follows the structure of the provided examples."
        )
    )

    generation_config = GenerationConfig(temperature=TEMPERATURE)

    # Function to get a response from the model
    def get_chat_response(chat: ChatSession, prompt: str) -> str:
        response = chat.send_message(prompt, generation_config=generation_config)
        return response.text

    # Loop 5 times to generate questions
    all_generated_questions = []  # Store all generated questions

    for i in range(N_LOOPS):
        print(f"Starting iteration {i + 1}...")

        # Select 5 random examples for the prompt
        selected_examples = random.sample(examples, 5)

        # Create the prompt
        prompt = (
            f"Here are some example test questions for {args.level}-level English:\n"
            f"{json.dumps(selected_examples, indent=4)}\n\n"
            f"Now generate exactly {N_QUESTIONS} new test questions for {args.level}-level English in the same format."
        )

        # Start a new chat session
        chat_session = model.start_chat()

        # Get the response
        response = get_chat_response(chat_session, prompt)

        try:
            # Clean and parse the response
            cleaned_response = response.strip().replace("```json", "").replace("```", "")
            response_json = json.loads(cleaned_response)

            # Append generated questions to the list
            all_generated_questions.extend(response_json)

        except json.JSONDecodeError as e:
            print("Failed to parse response as JSON. Debugging info:")
            print("Error:", e)
            print("Response:", repr(response))
            continue

    # Save all generated questions to a single JSON file
    with open(OUTPUT_FILE_PATH, "w") as output_file:
        json.dump(all_generated_questions, output_file, indent=4)

    print(f"All generated questions saved to {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()
