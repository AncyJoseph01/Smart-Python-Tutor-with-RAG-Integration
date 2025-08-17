# Use official Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install system dependencies (needed for psycopg2 / numpy / faiss etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY app/ ./app/

# Copy the FAISS index file if it exists
COPY app/output/textbook_index.faiss ./app/output/textbook_index.faiss

COPY app/output/text_chunks.pkl ./app/output/text_chunks.pkl
# Expose FastAPI port
EXPOSE 8000

# Default command to run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]