#!/bin/bash

set -e

# Build the image based on the Dockerfile
docker build -t diagnostic_test -f Dockerfile .

# Remove container if it exists
docker rm -f diagnostic_test 2>/dev/null || true

# Run data-label-cli container
docker run --rm -ti \
  --name diagnostic_test \
  -v "$(pwd)/../../../secrets:/secrets" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/text-generator.json" \
  diagnostic_test