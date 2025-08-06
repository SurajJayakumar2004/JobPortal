#!/bin/bash

# AppDeduplicator Build Script

echo "=== AppDeduplicator Build Script ==="
echo "Building Java application..."

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed or not in PATH"
    echo "Please install Maven and try again"
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH"
    echo "Please install Java 17+ and try again"
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo "Error: Java 17 or higher is required"
    echo "Current Java version: $JAVA_VERSION"
    exit 1
fi

echo "Java version: $(java -version 2>&1 | head -n 1)"
echo "Maven version: $(mvn -version | head -n 1)"

# Clean and build
echo "Cleaning previous builds..."
mvn clean

echo "Compiling and packaging..."
mvn package

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "Executable JAR created: target/AppDeduplicator.jar"
    echo ""
    echo "To run the application:"
    echo "java -jar target/AppDeduplicator.jar"
    echo ""
    echo "Or use the run script:"
    echo "./run.sh"
else
    echo "❌ Build failed!"
    exit 1
fi
