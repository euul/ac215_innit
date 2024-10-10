#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t datapipeline -f Dockerfile .


# Remove container if it exists
docker rm -f datapipeline 2>/dev/null || true


# Run data-label-cli container
docker run --rm -ti \
  --name datapipeline \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  datapipeline