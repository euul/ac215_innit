# Use the official Debian-hosted Python image
FROM python:3.11-slim-buster

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

# Add Pipfile, Pipfile.lock + python code
COPY Pipfile Pipfile.lock /app/

RUN pipenv sync

COPY . /app

# Entry point
#ENTRYPOINT ["/bin/bash"] #this is for debugging and MS5...probably

# Get into the pipenv shell
#CMD ["-c", "pipenv shell"] #this is for debugging
#CMD ["pipenv", "run", "python", "app.py"] #this is for MS5
#CMD ["/bin/sh", "-c", "echo 'Container is running'"]
