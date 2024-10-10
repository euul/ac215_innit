#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t webscrape -f Dockerfile .


# Remove container if it exists
docker rm -f webscrape 2>/dev/null || true


# Run data-label-cli container
docker run --rm -ti \
  --name webscrape \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  webscrape