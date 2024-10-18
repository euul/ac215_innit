## Milestone 2 Template

```
Welcome to Team Save the Penguin's Milestone 2! Remember to close your instances on GCP or you will kill more penguins!
```

#### Project Milestone 2 Organization

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
├── reports
│   ├── mockup_docs.pdf
│   └── statement_of_work.pdf
└── src
    ├── datapipeline
    │   ├── container_screenshot.png
    │   ├── dataloader.py
    │   ├── Dockerfile
    │   ├── docker-shell.sh
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── preprocess.py
    │   ├── Readme.md
    │   └── requirements.txt
    ├── docker-compose.yml
    ├── models
    │   ├── container_screenshot.png
    │   ├── Dockerfile
    │   ├── docker-shell.sh
    │   ├── fine_tuning_process.md
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── readme.md
    │   ├── requirements.txt
    │   └── train_model.py
    └── webscraping
        ├── container_screenshot.png
        ├── Dockerfile
        ├── Pipfile
        ├── Pipfile.lock
        ├── Readme.md
        ├── requirements.txt
        ├── run_scraper.sh
        ├── scrape_all_links.py
        ├── scrape_all_transcripts.py
        ├── target_links_teens.txt
        └── target_links.txt

```

# AC215 - Milestone2 - Innit: Immersive Language Learning App

**Team Members**
Christian Aagnes, James Cao and Alyssa Chang

**Group Name**
Save the Penguins

**Project**
In this project, we aim to develop an English language learning application that leverages online media sources to create an immersive learning experience, matching users with content at their proficiency level and allowing users to learn dynamically while engaging with everyday content.


### Milestone2 ###

In this milestone, we have the components for data scraping and data processing as well as a DeBERTA model capable of rating the difficulty of a given corpus.

**Data**
We gathered a dataset of approximately 1500 labeled texts of varying difficulty from the LearnEnglish British Council organization. The dataset has been scored on a private Google Cloud Bucket. Additionally, in further milestones, we plan to use generative AI to create more labeled example for our model to train on.

**Milestone 2 Containers and Overview**
The following documents contain an overview of each container, its components and how to run each container.
1. [webscraping](./src/webscraping/Readme.md)
2. [datapipline](./src/datapipeline/Readme.md)
3. [models](./src/models/readme.md)

**Notebooks/Reports**
This folder contains code that is not part of container such our application mockup, statement of work and some cursory EDA.

----