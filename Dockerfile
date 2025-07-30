# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y \
    # Build essentials for compiling Python packages
    build-essential \
    gcc \
    g++ \
    # Cairo dependencies
    libcairo2-dev \
    pkg-config \
    python3-dev \
    # Pango dependencies
    libpango1.0-dev \
    # Media dependencies
    ffmpeg \
    # Git for pip installs
    git \
    # LaTeX for mathematical rendering
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    # Additional dependencies
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY manim_agent/ ./manim_agent/
COPY api_server.py .

# Create directories for generated content
RUN mkdir -p generated_videos/media

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV USE_ADVANCED_ORCHESTRATOR=true

# Run the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]