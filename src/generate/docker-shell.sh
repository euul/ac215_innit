#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="generate_samples"

# Build the image with the target platform
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run the container, ensuring platform compatibility and passing arguments
docker run --rm -ti \
  --platform=linux/amd64 \
  --name $IMAGE_NAME \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/text-generator.json" \
  -p 8080:8080 \
  -e DEV=1 \
  $IMAGE_NAME python gen_samples.py --level A1 --n_samples 10
