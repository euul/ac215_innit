#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="innit-api-service-shivas"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT="innit-437518" 
export GCS_BUCKET_NAME="innit_articles_bucket"

# Create the Docker network if it doesn't already exist
docker network inspect innit-app-network >/dev/null 2>&1 || docker network create innit-app-network

# Build the Docker image based on the Dockerfile
# Uncomment the first line for standard builds, or the second for M1/M2 Macs
# docker build -t $IMAGE_NAME -f Dockerfile .
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-p 9000:9000 \
-e DEV=1 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/data-service-account.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
--network innit-app-network \
$IMAGE_NAME
