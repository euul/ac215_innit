# News Text Module

## Overview

This module scrapes news articles from the BBC News website (`https://www.bbc.com/news`), labels the articles' difficulty levels using our model, and uploads the labeled results to a GCP bucket as `bbc_news_articles_labeled.json`.

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

- Scrapes articles from the BBC News front page.
- Downloads model weights from GCP and infers the difficulty level of the articles.
- Uploads the labeled articles as bbc_news_articles_labeled.json to the specified GCP bucket.
