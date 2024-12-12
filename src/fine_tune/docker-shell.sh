#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t finetune -f Dockerfile .


# Remove container if it exists
docker rm -f finetune 2>/dev/null || true


# Run finetune container
docker run --rm -ti \
  --name finetune \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  finetune