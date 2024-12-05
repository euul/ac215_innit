#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define environment variables
export IMAGE_NAME="innit-frontend"
export API_URL="http://api-service:5001"  # Set the backend API URL for production

# Build the Docker image for the frontend
echo "Building the Docker image for the frontend with API URL: $API_URL..."
docker build -t $IMAGE_NAME --build-arg REACT_APP_API_URL=$API_URL .

# Create the network if it doesn't already exist
if ! docker network inspect innit-network >/dev/null 2>&1; then
    echo "Creating Docker network 'innit-network'..."
    docker network create innit-network
fi

# Remove any existing container with the same name to avoid conflicts
if [ "$(docker ps -aq -f name=innit-frontend)" ]; then
    echo "Removing existing container with the name 'innit-frontend'..."
    docker rm -f innit-frontend
fi

# Run the Docker container on the innit-network
echo "Running the Docker container for the frontend..."
docker run --rm --name innit-frontend -d \
  --network innit-network \
  -p 3000:80 \
  $IMAGE_NAME

echo "Frontend is running at http://localhost:3000"
