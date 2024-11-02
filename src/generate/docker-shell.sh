#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t generate -f Dockerfile .


# Remove container if it exists
docker rm -f generate 2>/dev/null || true


# Run models container
docker run --rm -ti \
  --name generate \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/text-generator.json" \
  generate