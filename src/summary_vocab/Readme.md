# Summary and Vocabulary

## Overview
Use Gemini to create summary and list of key vocabularies by level for the news and video scripts.

## Instructions

### 1. Running the Container
To start the container, use the following command:

```bash
sh docker-shell.sh
```

### 2. Executing the Script
Once inside the running container, execute the following command:

```python
python summary_vocab_news.py
```

This will start a batch prediction in GCP to get summary and key vocab by level for news articles


```python
python extract_results_news.py
```

This will append two keys 'summary' and 'vocab' to the original news articles json file in GCP.

