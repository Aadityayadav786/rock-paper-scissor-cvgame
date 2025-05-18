# Use official Python slim image
FROM python:3.12-slim

# Install required system dependencies (for OpenCV + Flask + Gunicorn)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \             # For OpenCV GUI support
    libglib2.0-0 \                # Dependency for OpenCV
    build-essential \            # Good to have for pip packages with C extensions
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port (for Railway or local run)
EXPOSE 8080

# Start the Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
