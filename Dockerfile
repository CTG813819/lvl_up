FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only essential application files
COPY app/ ./app/
COPY main_unified.py ./
COPY requirements.txt ./

# Create plugins directory and copy plugins if they exist
RUN mkdir -p ./plugins
COPY plugins ./plugins/ 2>/dev/null || true

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Expose port (using memory about user's preferred port 8000)
EXPOSE 8000

# Health check using ping endpoint and dynamic port
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Let Railway handle the startup command (railway.toml will override this)
CMD ["uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000"]