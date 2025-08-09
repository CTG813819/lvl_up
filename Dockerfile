# Pin Python to 3.11 to avoid numpy build issues and pkgutil.ImpImporter incompatibilities
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy build requirements first
COPY requirements-build.txt .

# Install build dependencies first
RUN pip install --no-cache-dir -r requirements-build.txt

# Copy main requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only essential application files
COPY app/ ./app/
COPY plugins/ ./plugins/
COPY main_unified.py ./
COPY requirements.txt ./

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Expose port (using memory about user's preferred port 8000)
EXPOSE 8000

# Health check using ping endpoint and dynamic port
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Let Railway handle the startup command (railway.toml will override this)
CMD ["uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000"]