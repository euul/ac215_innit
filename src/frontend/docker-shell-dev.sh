#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Define environment variables
export IMAGE_NAME="innit-frontend-dev"

# Build the Docker image for development
echo "Building the Docker image for the frontend (development mode)..."
docker build -t $IMAGE_NAME -f Dockerfile.dev .

# Create the network if it doesn't already exist
docker network inspect innit-network >/dev/null 2>&1 || docker network create innit-network

# Remove any existing container with the same name to avoid conflicts
if [ "$(docker ps -aq -f name=innit-frontend-dev)" ]; then
    echo "Removing existing container with the name 'innit-frontend-dev'..."
    docker rm -f innit-frontend-dev
fi

# Run the Docker container in development mode with volume mounts for live reloading
echo "Running the Docker container for the frontend (development mode)..."
docker run --rm --name innit-frontend-dev -d \
  --network innit-network \
  -v $(pwd):/app \
  -v /app/node_modules \
  -p 3000:3000 \
  $IMAGE_NAME

echo "Frontend development server is running at http://localhost:3000"
