#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t sum-vocab -f Dockerfile .

# Remove container if it exists
docker rm -f sum-vocab 2>/dev/null || true

# Run data-label-cli container
docker run --rm -ti \
  --name sum-vocab \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/text-generator.json" \
  sum-vocab