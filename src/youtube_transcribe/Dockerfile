# Use the official Python image with Debian as a base
FROM euxl/datapipeline:latest

# Tell pipenv where the shell is.
# This allows us to use "pipenv shell" as a container entry point.
ENV PYENV_SHELL=/bin/bash

# Ensure we have an up-to-date baseline, install dependencies
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libxtst6 \
    libx11-xcb1 \
    libxi6 \
    libxcomposite1 \
    libxrandr2 \
    build-essential \
    git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

# Install Google Chrome version 114.0.5735.90
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt --fix-broken install -y
    
# Install ChromeDriver version 114.0.5735.90
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set the environment variable to help Selenium locate Chrome
ENV CHROME_BIN=/opt/google/chrome/chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

WORKDIR /app

# Add Pipfile and Pipfile.lock + Python code
ADD Pipfile Pipfile.lock /app/

# Install Python dependencies using pipenv
RUN pipenv sync

# Add the application code
ADD . /app

# Entry point: use bash and run pipenv shell by default
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "pipenv shell"]
