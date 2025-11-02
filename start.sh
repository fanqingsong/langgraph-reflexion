#!/bin/bash

# Start script for Reflexion Agent application

set -e

echo "🚀 Starting Reflexion Agent application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file with the following variables:"
    echo ""
    echo "   # For Azure OpenAI (recommended):"
    echo "   AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here"
    echo "   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
    echo "   AZURE_OPENAI_API_VERSION=2024-02-15-preview"
    echo "   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4"
    echo "   TAVILY_API_KEY=your_tavily_api_key_here"
    echo ""
    echo "   # Or for standard OpenAI:"
    echo "   # OPENAI_API_KEY=your_openai_api_key_here"
    echo "   # TAVILY_API_KEY=your_tavily_api_key_here"
    echo ""
    echo "   # Optional:"
    echo "   LANGCHAIN_API_KEY=your_langchain_api_key_here"
    echo "   LANGCHAIN_TRACING_V2=true"
    echo "   LANGCHAIN_PROJECT=reflexion agent"
    exit 1
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Error: docker compose is not available"
    exit 1
fi

# Build and start containers
echo "🔨 Building Docker image..."
docker compose build

echo "🚀 Starting containers..."
docker compose up -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker compose ps | grep -q "Up"; then
    echo "✅ Reflexion Agent application is running!"
    echo ""
    echo "📡 Access the application at:"
    echo "   - API: http://localhost:2024"
    echo "   - API Docs: http://localhost:2024/docs"
    echo "   - LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
    echo ""
    echo "📊 View logs with: docker compose logs -f"
    echo "🛑 Stop with: ./stop.sh"
else
    echo "❌ Error: Service failed to start"
    echo "📋 Check logs with: docker compose logs"
    exit 1
fi

