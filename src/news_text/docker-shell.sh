#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t news-text -f Dockerfile .


# Remove container if it exists
docker rm -f news-text 2>/dev/null || true


# Run data-label-cli container
docker run --rm -ti \
  --name news-text \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  --memory=4g \
  --cpus=2 \
  news-text