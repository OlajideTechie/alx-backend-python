# Start with a lightweight Python base image
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/app/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies (MySQL client, build tools)
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        libmariadb-dev && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python -m venv /app/venv

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files into the image
COPY . .

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose Django’s default port
EXPOSE 8000

# Use a non-root user (security best practice)
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Run the Django app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]