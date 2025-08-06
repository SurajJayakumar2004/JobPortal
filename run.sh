#!/bin/bash

# AppDeduplicator Run Script

echo "=== Starting AppDeduplicator ==="

# Check if JAR file exists
JAR_FILE="target/AppDeduplicator.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "Error: $JAR_FILE not found"
    echo "Please build the application first:"
    echo "./build.sh"
    exit 1
fi

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH"
    exit 1
fi

# Run the application
echo "Running AppDeduplicator..."
echo "JAR file: $JAR_FILE"
echo ""

# Simple execution - Swing works out of the box
java -jar "$JAR_FILE" "$@"

echo ""
echo "AppDeduplicator session ended."