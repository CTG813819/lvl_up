FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

<<<<<<< HEAD
# Copy requirements first for better caching
COPY requirements.txt .
=======
# Copy the ai-backend-python directory contents
COPY ai-backend-python/requirements.txt .
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copy only essential application files
COPY app/ ./app/
COPY main_unified.py ./
COPY requirements.txt ./
=======
# Copy application code from ai-backend-python
COPY ai-backend-python/ .
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

<<<<<<< HEAD
# Expose port (using memory about user's preferred port 8000)
=======
# Expose port
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

<<<<<<< HEAD
# Start the application directly with uvicorn on port 8000
CMD ["python", "-m", "uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000"]
=======
# Start the application using the startup script that prioritizes main_unified.py
CMD ["python", "start_app.py"] 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
