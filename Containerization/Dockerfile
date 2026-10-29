FROM docker.io/library/python:3.14-slim-trixie

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    STORAGE_DIR=/data

# Set working directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
