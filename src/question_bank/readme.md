# Question Bank

## Overview

This module creates a test question bank for a diagnostic test that determines the user's proficiency level. It uses English Unlimited placement test questions as examples to create few-shot prompts and leverages Gemini (`gemini-1.5-pro-002`) to generate synthetic test questions. These generated questions are added to the test bank.

_Note: English Unlimited is a comprehensive English language course developed by Cambridge University Press, designed for adult learners ranging from beginner (A1) to advanced (C1) levels._

## Instructions

### 1. Running the Container

To start the container, use the following command:

```bash
sh docker-shell.sh
```

### 2. Executing the Script

Once inside the running container, execute the following command:

```python
python cli.py
```

#### What the Script Does:

For each proficiency level:

- Select test questions of the corresponding level.
- Randomly pick 5 questions from the sample to use as prompts.
- Generate 50 similar test questions using Gemini.

Upload the generated questions to a GCP bucket at the following location:

```bash
./generated_questions/generated_questions_{LEVEL}.json
```

For each level:

- take the test question of that level, randomly select 5 questions from the sample, use them for prompt
- ask Gemini to generate 50 similar samples.
  Uploads the generated samples to GCP bucket with blob './generated*questions/generated_questions*{LEVEL}.json'

#### Prompt Used

The following prompt is designed to instruct the model:

```python
model = GenerativeModel(
    model_name=MODEL_ID,
    system_instruction=(
        "You are an English teacher specializing in compiling placement test banks. "
        "Your task is to generate exactly {N_QUESTIONS} test questions for an {LEVEL}-level English test. "
        "Each question should include: a question text, three answer choices (A, B, C), the correct answer, and the level. "
        "Ensure the output is in JSON format and follows the structure of the provided examples."
    )
)
prompt = (
    f"Here are some example test questions for {LEVEL}-level English:\n"
    f"{json.dumps(selected_examples, indent=4)}\n\n"
    f"Now generate exactly {N_QUESTIONS} new test questions for {LEVEL}-level English in the same format."
)
```

#### Example of Generated Question

```json
{
  "question": "_____ you like a cup of tea?",
  "choices": ["Do", "Would", "Are"],
  "answer": "B",
  "level": "A1"
}
```
