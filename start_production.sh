#!/bin/bash

# Production startup script for Manim Agent

echo "🚀 Starting Manim Agent in Production Mode..."
echo "=============================================="

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set"
    echo "Please set it in your .env file or environment"
    exit 1
fi

# Create necessary directories
mkdir -p generated_videos/media

# Start with gunicorn for production
echo "🎬 Starting API server..."
gunicorn api_server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -