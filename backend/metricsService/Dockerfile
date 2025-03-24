FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# Installs essential tools for compiling software from source, often needed for Python package dependencies.(build-essential)
# Removes the package lists downloaded during the update to reduce the image size.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the PATH environment variable to include /app
ENV PATH="/app:${PATH}"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the rest of the application
COPY ./src/ /app/src/

RUN cd /app/src

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]