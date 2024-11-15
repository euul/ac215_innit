#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t yt-transcript -f Dockerfile .


# Remove container if it exists
docker rm -f yt-transcript 2>/dev/null || true


# Run data-label-cli container
docker run --rm -ti \
  --name yt-transcript \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  yt-transcript