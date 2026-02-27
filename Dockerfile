
# 🐳 Menir V5 Universal Dockerfile
# Base Image: Python 3.11 Slim (Debian-based) for balance of size and compatibility.

FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-root user "menir"
RUN useradd -m -s /bin/bash menir

# Set work directory
WORKDIR /app

# Install system dependencies (curl for healthchecks if needed, git for some pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install watchdog tenacity google-generativeai

# Copy Critical Scripts & Source Code
# Note: In dev mode, we usually bind mount /app/src, but copying ensures the image is standalone.
COPY src/ /app/src/
COPY verify_docker.py /app/verify_docker.py
COPY .env.example /app/.env.example

# Create Directories for Volumes and set permissions
RUN mkdir -p /app/Menir_Inbox /app/logs && \
    chown -R menir:menir /app/Menir_Inbox /app/logs /app/src

# Remove root privileges
USER menir

# Default Command (Overridden by docker-compose)
CMD ["python", "verify_docker.py"]
