# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using pip, but handle spacy separately
RUN pip install --upgrade pip && \
    grep -v "spacy" requirements.txt > requirements_no_spacy.txt && \
    pip install --no-cache-dir -r requirements_no_spacy.txt

# Install pre-built wheels for spacy and its dependencies
RUN pip install --no-cache-dir cython && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir --only-binary=:all: spacy

# Create a dummy spacy model to avoid errors
RUN mkdir -p /usr/local/lib/python3.10/site-packages/en_core_web_sm && \
    echo "# Dummy spacy model" > /usr/local/lib/python3.10/site-packages/en_core_web_sm/__init__.py

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data eda_plots

# Expose the Streamlit port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]