# Use Python 3.12 slim image
FROM python:3.12-slim

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the port
EXPOSE 5000

# Start the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
