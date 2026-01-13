#!/bin/bash
# --- Standard Deployment Script for AgenticArchitect (Local & CI) ---
set -e

# Define project root (one level up from infra/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="k3d-registry.localhost"
REGISTRY_PORT="5000"

# Image names
ARCHITECT_IMAGE="agentic-architect-local:latest"
OLLAMA_IMAGE="custom-ollama-gemma:latest"

echo "🛠️ Project Root: $PROJECT_ROOT"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "📥 Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Create cluster with local registry (essential for heavy LLM images)
if ! k3d cluster get $CLUSTER_NAME &>/dev/null; then
    echo "🏗️ Creating cluster $CLUSTER_NAME with local registry..."
    k3d cluster create $CLUSTER_NAME \
        --registry-create "$REGISTRY_NAME:$REGISTRY_PORT" \
        --k3s-arg '--disable=traefik@server:*' \
        -p "8080:80@loadbalancer" \
        --wait
fi

# 3. Build images with local registry tags
echo "📦 Building images..."
docker build -t "$REGISTRY_NAME:$REGISTRY_PORT/$ARCHITECT_IMAGE" \
    -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

docker build -t "$REGISTRY_NAME:$REGISTRY_PORT/$OLLAMA_IMAGE" \
    -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"

# 4. Push directly to local registry (disk-efficient compared to 'import')
echo "🚀 Pushing images to local registry..."
docker push "$REGISTRY_NAME:$REGISTRY_PORT/$ARCHITECT_IMAGE"
docker push "$REGISTRY_NAME:$REGISTRY_PORT/$OLLAMA_IMAGE"

# 5. Apply Kubernetes manifests
echo "⎈ Applying manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

echo "✅ Deployment successful! Your infrastructure is ready."