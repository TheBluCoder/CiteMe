FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# Installs essential tools for compiling software from source, often needed for Python package dependencies.(build-essential)
# Removes the package lists downloaded during the update to reduce the image size.
RUN apt-get update && apt-get install -y \
    build-essential \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set the PATH environment variable to include /app
ENV PATH="/app:${PATH}"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY ./scripts/ /app/scripts/
COPY ./src/ /app/src/
COPY ./app.py /app/app.py
COPY ./__init__.py /app/__init__.py

# Create a directory for runtime configuration
RUN mkdir -p /app/config

# Install playwright
RUN playwright install && playwright install-deps 

# Expose the port the app runs on
EXPOSE 8000

# Start both cron and the FastAPI application
CMD ["sh", "-c", "cron && uvicorn app:app --host 0.0.0.0 --port 8000"] 