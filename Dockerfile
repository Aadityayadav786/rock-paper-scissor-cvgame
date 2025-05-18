# Use Python base image
FROM python:3.12-slim

# Install required system dependencies (including libGL)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (for Railway)
EXPOSE 8080

# Start the app with gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
