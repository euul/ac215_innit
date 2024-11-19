#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t question-bank -f Dockerfile .


# Remove container if it exists
docker rm -f question-bank 2>/dev/null || true


# Run data-label-cli container
docker run --rm -ti \
  --name question-bank \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/text-generator.json" \
  --memory=10g \
  --cpus=2 \
  question-bank