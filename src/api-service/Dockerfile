# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install supervisord and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Copy supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports for FastAPI (8000) and Flask (5001)
EXPOSE 8000
EXPOSE 5001

# Use supervisord to manage both processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
