#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t models -f Dockerfile .


# Remove container if it exists
docker rm -f models 2>/dev/null || true


# Run models container
docker run --rm -ti \
  --name models \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  models