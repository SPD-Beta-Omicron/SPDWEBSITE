# Python/Django code located in /app
# Media, static, and other files stored in /data

FROM docker.io/library/python:3.14-slim-trixie

LABEL org.opencontainers.image.source="https://github.com/SPD-Beta-Omicron/SPDWEBSITE"

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

# Create a non-root user and set permissions for the storage directory
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin app \
    && mkdir -p /data \
    && chown app:app /data

# Copy application code
COPY --chmod=755 Containerization/container-entrypoint.sh /usr/local/bin/
COPY django/ .

USER app

# Documentation
EXPOSE 8000

# Set entrypoint, listen on port 8000, and run the application with Gunicorn
ENTRYPOINT ["container-entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--access-logfile", "-"]