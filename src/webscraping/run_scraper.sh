#!/bin/bash

# Set the Google Application Credentials environment variable
export GOOGLE_APPLICATION_CREDENTIALS="../../../secrets/data-service-account.json"

# Activate the conda environment if needed (uncomment and modify the path if necessary)
# source activate your_env_name

# Run the Python script
python scrape_all_links.py
python scrape_all_transcripts.py

# Optional: Print a message when the script finishes
echo "Data scraping and upload completed."
