# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    libcairo2-dev \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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