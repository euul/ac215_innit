#!/bin/bash

echo "Container is running!!!"

# Authenticate gcloud using service account
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS

# Set GCP Project Details (add --quiet to skip confirmation)
gcloud config set project $GCP_PROJECT --quiet

# Configure GCR
gcloud auth configure-docker gcr.io -q

/bin/bash
