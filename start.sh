#!/bin/bash

# Job Portal Application Startup Script

echo "🚀 Starting Job Portal Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration!"
fi

# Start the FastAPI application
echo "🎯 Starting FastAPI server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000