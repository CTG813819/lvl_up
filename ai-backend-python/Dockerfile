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

# Copy only essential application files (explicit to avoid .dockerignore issues)
COPY app/ ./app/
COPY main_unified.py ./
COPY start_app.py ./
COPY Procfile ./
COPY railway.toml ./
COPY railway.json ./
COPY nixpacks.toml ./

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Expose port (using memory about user's preferred port 8000)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application directly with uvicorn
CMD ["python", "-m", "uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000"]