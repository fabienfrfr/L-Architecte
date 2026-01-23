#!/bin/bash
set -e

# --- Configuration ---
REGISTRY="ghcr.io/fabienfrfr"
ARCHITECT_IMG="$REGISTRY/agentic-architect:latest"
OLLAMA_IMG="$REGISTRY/custom-ollama-gemma:latest"

echo "🚀 Starting Production Build & Push for AgenticArchitect..."

# 1. Check for GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is not set."
    echo "Please run: export GITHUB_TOKEN=your_pat_token"
    exit 1
fi

# 2. Build Images
# Using the project root as context to allow COPY commands to work correctly
echo "📦 Building Docker images..."
docker build -t $ARCHITECT_IMG -f apps/architect/Dockerfile .
docker build -t $OLLAMA_IMG -f infra/Ollama.Dockerfile .

# 3. Registry Authentication & Push
echo "🔐 Logging into GHCR..."
echo $GITHUB_TOKEN | docker login ghcr.io -u fabienfrfr --password-stdin

echo "📤 Pushing images to GitHub Packages..."
docker push $ARCHITECT_IMG
docker push $OLLAMA_IMG

echo "✅ Release Successful! Images are now live on GHCR."
echo "👉 You can now run Pulumi to update the cluster."