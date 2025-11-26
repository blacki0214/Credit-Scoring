#!/bin/bash
# Startup script for Credit Scoring API

echo "============================================"
echo "   Credit Scoring API - Startup Script     "
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"

# Check if model files exist
if [ ! -f "models/lgb_model_optimized.pkl" ]; then
    echo "❌ Error: Model file not found"
    echo "Please ensure models/lgb_model_optimized.pkl exists"
    exit 1
fi

if [ ! -f "models/ensemble_comparison_metadata.pkl" ]; then
    echo "❌ Error: Metadata file not found"
    echo "Please ensure models/ensemble_comparison_metadata.pkl exists"
    exit 1
fi

echo "✅ Model files found"

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down

# Build and start
echo ""
echo "Building and starting API..."
docker-compose up --build -d

# Wait for container to be ready
echo ""
echo "Waiting for API to be ready..."
sleep 5

# Check if container is running
if [ "$(docker ps -q -f name=credit-scoring-api)" ]; then
    echo "✅ Container is running"
    
    # Test health endpoint
    echo ""
    echo "Testing health endpoint..."
    if curl -f -s http://localhost:8000/api/health > /dev/null; then
        echo "✅ API is healthy"
        echo ""
        echo "============================================"
        echo "🎉 API is ready!"
        echo "============================================"
        echo ""
        echo "📚 Documentation: http://localhost:8000/docs"
        echo "🏥 Health Check:  http://localhost:8000/api/health"
        echo "🔍 Logs:          docker-compose logs -f"
        echo ""
        echo "To stop: docker-compose down"
        echo "============================================"
    else
        echo "⚠️  Container is running but API is not responding"
        echo "Check logs: docker-compose logs"
    fi
else
    echo "❌ Container failed to start"
    echo "Check logs: docker-compose logs"
    exit 1
fi
