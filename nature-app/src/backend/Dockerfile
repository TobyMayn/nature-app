# Use a specific Python base image (adjust version as needed)
# If you need CUDA/GPU support, you'd use an nvidia/cuda or pytorch/pytorch base image
# e.g., FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
FROM python:3.12-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for geospatial libraries
# gdal-bin: Geospatial Data Abstraction Library command-line tools
# libgdal-dev: Development files for GDAL
# build-essential: For compiling C extensions (e.g., for numpy, shapely)
# libspatialindex-dev: For R-tree spatial indexing used by geopandas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    build-essential \
    libspatialindex-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Set environment variables for FastAPI and Uvicorn (optional, good practice)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose the port your FastAPI app runs on
EXPOSE 80

# Command to run your application using Uvicorn
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
