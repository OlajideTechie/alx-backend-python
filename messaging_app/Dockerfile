# Use a smaller, faster base image
FROM python:3.10-slim

# Avoid apt-get interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (MySQL client, build tools)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        libmariadb-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Django port
EXPOSE 8000

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]