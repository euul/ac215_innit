## Milestone 4

```
Welcome to Team Save the Penguin's Milestone 4! Remember to close your instances on GCP or you will kill more penguins! 🐧
```

![Integration Tests](https://github.com/euul/ac215_innit//actions/workflows/integration.yml/badge.svg?branch=milestone4)

#### Project Milestone 4 Organization

```
├── LICENSE
├── notebooks
│   ├── app
│   │   └── data
│   │       ├── scraped_all_content.json
│   │       └── scraped_all_content_teens.json
│   └── eda.ipynb
├── README.md
├── references
├── midterm_presentation
├── reports
│   ├── mockup_docs.pdf
│   └── statement_of_work.pdf
└── src
    ├── datapipeline
    ├── models
    ├── webscraping
    ├── generate
    ├── fine_tune
    ├── question_bank
    ├── youtube_transcribe
    ├── news_text
    ├── api-service
    ├── frontend
    └── docker-compose.yml

```

# AC215 - Milestone4 - Innit: Immersive Language Learning App

**Team Members**
Christian Aagnes, James Cao and Alyssa Chang

**Group Name**
Save the Penguins🐧

**Project**
In this project, we aim to develop an English language learning application that leverages online media sources to create an immersive learning experience, matching users with content at their proficiency level and allowing users to learn dynamically while engaging with everyday content.

**Data**
We gathered a dataset of approximately 1500 labeled texts of varying difficulty from the LearnEnglish British Council organization. The dataset has been scored on a private Google Cloud Bucket. Additionally, we used generative AI to create more labeled examples. Then we finetuned our base DeBeRTa classification model with these labeled examples in order to improve our model accuracy and fix our data imbalance.

### Milestone4

In this milestone, we added new components to scrape bbc news for articles and Youtube for videos based on search keywords. We also added components to generate LLM-generate text at specific language levels and then we fine-tuned our base model with these additional data points.

**Milestone4 Containers and Overview**
The following documents contain an overview of each container, its components and how to run each container.

1. [webscraping](./src/webscraping/README.md)
2. [datapipline](./src/datapipeline/README.md)
3. [models](./src/models/README.md)
4. [fine_tune](./src/fine_tune/README.md)
5. [generate](./src/generate/README.md)
6. [youtube_transcribe](./src/models/README.md)
7. [news_text](./src/news_text/README.md)
8. [question_bank](./src/question_bank/README.md)
9. [api-service](./src/api-service/README.md)
10. [frontend](./src/frontend/README.md)

---
