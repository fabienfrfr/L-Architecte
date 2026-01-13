#!/bin/bash
# --- Standard Deployment Script for AgenticArchitect (Local & CI) ---
set -e

# Determine project root (one level up from infra/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
IMAGE_NAME="agentic-architect-local:latest"

echo "🛠️ Project Root: $PROJECT_ROOT"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "📥 Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Create cluster
if ! k3d cluster get $CLUSTER_NAME &>/dev/null; then
    echo "🏗️ Creating cluster $CLUSTER_NAME..."
    k3d cluster create $CLUSTER_NAME \
        --k3s-arg '--disable=traefik@server:*' \
        -p "8080:80@loadbalancer" \
        --wait
fi

# 3. Build using the specific Dockerfile in apps/architect
echo "📦 Building $IMAGE_NAME..."
docker build -t $IMAGE_NAME \
    -f "$PROJECT_ROOT/apps/architect/Dockerfile" \
    "$PROJECT_ROOT"

# 4. Import and Deploy
echo "📥 Importing to k3d..."
k3d image import $IMAGE_NAME -c $CLUSTER_NAME

echo "⎈ Applying manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

echo "✅ Deployment successful!"