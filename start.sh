#!/bin/bash

# AI-Powered Job Portal Startup Script
echo "🚀 Starting AI-Powered Job Portal..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if uvicorn is installed
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "❌ uvicorn not found in virtual environment. Please run ./setup.sh first."
    exit 1
fi

# Start the application
echo "📡 Starting server at http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📖 Alternative docs: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
