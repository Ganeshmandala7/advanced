FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY fexsics/ ./fexsics/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FEXSICS_DATA_DIR=/data

# Expose port for API (if needed)
EXPOSE 8000

# Default command
CMD ["python", "-m", "fexsics"]
