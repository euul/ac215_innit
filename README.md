## Milestone 5

Welcome to Team Save the Penguin's Milestone 5! Remember to close your instances on GCP or you will kill more penguins! 🐧

![Integration Tests](https://github.com/euul/ac215_innit//actions/workflows/integration.yml/badge.svg?branch=main)

#### Project Milestone 5 Organization

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
│   ├── midterm_Save_the_Penguins.pdf
├── reports
│   ├── mockup_docs.pdf
│   └── statement_of_work.pdf
│   └── app_design.pdf
└── src
    ├── datapipeline
    ├── models
    ├── webscraping
    ├── generate
    ├── fine_tune
    ├── question_bank
    ├── youtube_transcribe
    ├── news_text
    ├── diagnostic_test
    ├── summarize_vocab
    ├── api-service
    ├── frontend
    └── deployment
    └── docker-compose.yml
└── .github/workflows
    ├── integration.yml
    ├── app_deploy.yml
    ├── ml_workflow.yml

```

# AC215 - Milestone 5 - Innit: Immersive Language Learning App

**Team Members**
Christian Aagnes, James Cao and Alyssa Chang

**Group Name**
Save the Penguins🐧

**Project**
In this project, we aim to develop an English language learning application that leverages online media sources to create an immersive learning experience, matching users with content at their proficiency level and allowing users to learn dynamically while engaging with everyday content.

**Data**
We gathered a dataset of approximately 1500 labeled texts of varying difficulty from the LearnEnglish British Council organization. The dataset has been scored on a private Google Cloud Bucket. Additionally, we used generative AI to create more labeled examples. Then we finetuned our base DeBeRTa classification model with these labeled examples in order to improve our model accuracy and fix our data imbalance.

### Milestone 5

In this milestone, we added new components to scrape bbc news for articles and Youtube for videos based on search keywords. We also added components to generate LLM-generate text at specific language levels and then we fine-tuned our base model with these additional data points.

**Milestone 5 Containers and Overview**
The following documents contain an overview of each container, its components and how to run each container.

1. [webscraping](./src/webscraping/Readme.md)
2. [datapipeline](./src/datapipeline/Readme.md)
3. [models](./src/models/readme.md)
4. [fine_tune](./src/fine_tune/readme.md)
5. [generate](./src/generate/readme.md)
6. [youtube_transcribe](./src/youtube_transcribe//README.md)
7. [news_text](./src/news_text/readme.md)
8. [question_bank](./src/question_bank/readme.md)
9. [diagnostic_test](./src/diagnostic_test/README.md)
10. [summarize_vocab](.src/summarize_vocab/README.md)
11. [api-service](./src/api-service-shivas/README.md)
12. [frontend](./src/frontend-shivas/README.md)
13. [deployment](./src/deployment/README.md)

**Github Actions for Continuous Integration and Deployment**
There are three Github workflows that assist with CI/CD of our language learning app. To briefly summarize the function of each workflow and how to trigger them:

1. **Code Building, Linting and Automated Testing**: The workflow will run unit tests across each container to ensure code quality and coverage. This workflow will run after each push, regardless of the trigger. This is intentionally done to ensure that all changes to the codebase align with proper linting and validation. To run this workflow, add `"/CI-test"` to your comment message to trigger this action.
2. **Kubernetes and Ansible Playbooks for Automated App Deployment**: This workflow will run an Ansible playbook to build and push the images related to app deployment (frontend and api-service) and then **update** an already existing Kubernetes cluster (containing the deployed app) with the changes to the frontend and backend portions of the app. This workflow is designed with the intention of already having the app deployed and running on a Google Cloud Cluster. In other words, this is how we would update our app dynamically if we were bring our app live and connected for users. To run this workflow, add `"/deploy-app"` to your comment message to trigger this action.

**To see verify this action works: please look at commit hash `3845bf4`.**

3. **Automated Labeling/Updates of App Database (ML Workflow)**: This workflow will focus on updating our production build to reflect changes/updates in media from the internet. Put simply, the following will be run when this workflow is triggered:

a) Scrape new  articles and videos (from our selected sources) every week.

b) Use the model to perform the inference step and label these new examples with English difficulty level.

c) Call Gemini (with the appropriate prompts) to generate the key vocabulary, summary and QA for each new article.

d) Add these labeled examples to the GCP bucket.

We would ideally run this workflow after a specific time interval to ensure that our app's database remains updated. If we were to continue running our production build, ideally, we would like to run this label/update workflow every week. To run this workflow, add `"/refresh_news"` to your comment message to trigger this action.

**To see verify this action works: please look at commit hash `d6821aa`.**

---
