# Use the official Debian-hosted Python image
FROM python:3.11-slim

# Install required system packages
ARG DEBIAN_PACKAGES="build-essential git screen vim"

# Prevent apt from showing prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set default locale for Python
ENV LANG=C.UTF-8

# Set default shell for pipenv
ENV PYENV_SHELL=/bin/bash

# Disable Python output buffering (logs appear in real-time)
ENV PYTHONUNBUFFERED=1

# Install system dependencies, pip, pipenv, and create a non-root user
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

# Switch to the non-root user
USER app
WORKDIR /app

# Copy Pipfile and Pipfile.lock for dependency installation
ADD --chown=app:app Pipfile Pipfile.lock /app/

# Install Python dependencies from Pipfile.lock
RUN pipenv sync

# Add application source code
ADD --chown=app:app . /app

# Set the entry point to the custom script
ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
