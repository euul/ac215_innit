# Use the pre-built Docker image as the base
FROM euxl/datapipeline:base-v1.1.0
# FROM python:3.11-slim-buster

# Tell pipenv where the shell is.
# This allows us to use "pipenv shell" as a container entry point.
ENV PYENV_SHELL=/bin/bash

# Ensure we have an up to date baseline, install dependencies
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app
WORKDIR /app

RUN mkdir -p /app/data
# Add Pipfile, Pipfile.lock + python code
ADD Pipfile Pipfile.lock /app/

RUN pipenv sync

ADD . /app
# # Entry point
# ENTRYPOINT ["/bin/bash"]

# # Get into the pipenv shell
# CMD ["-c", "pipenv shell"]