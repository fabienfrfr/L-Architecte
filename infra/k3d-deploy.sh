#!/bin/bash
# --- Deployment Script for AgenticArchitect (Local & CI) ---
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "📥 Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Delete existing cluster if any
k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true

# 3. Create cluster WITHOUT registry (simpler, faster)
echo "🏗️ Creating cluster $CLUSTER_NAME..."
k3d cluster create "$CLUSTER_NAME" \
    --k3s-arg '--disable=traefik@server:*' \
    -p "8080:80@loadbalancer" \
    --wait

# 4. Build images with LOCAL tags (no registry)
echo "📦 Building images..."
docker build -t "custom-ollama-gemma:latest" -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"
docker build -t "agentic-architect-local:latest" -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

# 5. Import images DIRECTLY into the cluster (no push/pull)
echo "🚀 Importing images into cluster..."
k3d image import custom-ollama-gemma:latest -c "$CLUSTER_NAME"
k3d image import agentic-architect-local:latest -c "$CLUSTER_NAME"

# 6. Apply Kubernetes manifests
echo "⎈ Applying manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

echo "✅ Done. Access TheArchitect at http://localhost:8080"
