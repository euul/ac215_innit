# Exit immediately if a command exits with a non-zero status
set -e

# Define environment variables
export IMAGE_NAME="innit-frontend"

# Build the Docker image for the frontend
echo "Building the Docker image for the frontend..."
docker build -t $IMAGE_NAME .

# Create the network if it doesn't already exist
docker network inspect innit-network >/dev/null 2>&1 || docker network create innit-network

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
