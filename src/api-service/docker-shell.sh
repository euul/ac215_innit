#!/bin/bash

set -e  # Exit on any error

# Define environment variables
export IMAGE_NAME="api-service"
export GCP_BUCKET_NAME="innit_articles_bucket"

# Build the Docker image
echo "Building the Docker image for $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Create the network if it doesn't already exist
if ! docker network inspect innit-network >/dev/null 2>&1; then
  echo "Creating Docker network 'innit-network'..."
  docker network create innit-network
fi

# Remove any existing container with the same name
if [ "$(docker ps -aq -f name=api-service)" ]; then
  echo "Removing existing container 'api-service'..."
  docker rm -f api-service
fi

# Run the Docker container
echo "Starting the Docker container for $IMAGE_NAME..."
docker run -d --name api-service \
  -v "$(pwd)/../../../secrets:/secrets" \
  -v "$(pwd)/yt_transcripts:/app/yt_transcripts" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  -e GCP_BUCKET_NAME="$GCP_BUCKET_NAME" \
  --network innit-network \
  -p 8000:8000 \
  -p 5001:5001 \
  $IMAGE_NAME

echo "You can view logs using: docker logs -f api-service"
