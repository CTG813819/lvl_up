FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ .

# Create a script to run the app in headless mode
RUN echo '#!/bin/bash\nxvfb-run -a python main.py' > run_app.sh && chmod +x run_app.sh

# Expose port for communication
EXPOSE 9000

# Run the application
CMD ["./run_app.sh"] 