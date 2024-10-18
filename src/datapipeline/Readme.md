# Data Preprocessing and Loader Module

## Overview
This module is designed to preprocess and load datasets for machine learning tasks. It handles the combination of multiple JSON files, data cleaning, dataset creation, and splitting the data into training, validation, and test sets. It also supports uploading datasets to Google Cloud Platform (GCP).

### Main Components
- **Data Loading**: Downloads JSON data from a GCP bucket and saves it locally for further processing.
- **Preprocessing**: Combines multiple JSON files (adult and teens data) into a single dataframe, cleans the data by removing invalid entries, and prepares the data for machine learning tasks by converting it into a pytorch datasets. It splits the dataset into training, validation, and test sets, and uploads the resulting datasets to Google Cloud Platform (GCP) for storage and future use.

## Instructions

### 1. Running the Container
To start the container, execute the following command:
```bash
sh docker-shell.sh
```
Inside the running container, load and preprocess datasets by executing:

```python
python dataloader.py
python preprocess.py
```