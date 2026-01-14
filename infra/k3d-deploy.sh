#!/bin/bash
# --- Standard Deployment Script for AgenticArchitect (Local & CI) ---
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="k3d-registry.localhost"
REGISTRY_PORT="5000"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Delete existing cluster and registry (cleanup)
k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
k3d registry delete "$REGISTRY_NAME" 2>/dev/null || true

# 3. Create a local ephemeral registry
echo "Creating local registry..."
k3d registry create "$REGISTRY_NAME" --port "$REGISTRY_PORT"

# 4. Create cluster with registry access
echo "Creating cluster with registry access..."
k3d cluster create "$CLUSTER_NAME" \
    --registry-use "k3d-$REGISTRY_NAME:$REGISTRY_PORT" \
    --k3s-arg '--disable=traefik@server:*' \
    -p "8080:80@loadbalancer" \
    --wait

# 5. Build images with correct tags
echo "Building images..."
docker build -t "$REGISTRY_NAME:$REGISTRY_PORT/custom-ollama-gemma:latest" -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"
docker build -t "$REGISTRY_NAME:$REGISTRY_PORT/agentic-architect-local:latest" -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

# 6. Push images to local registry
echo "Pushing images to local registry..."
docker push "$REGISTRY_NAME:$REGISTRY_PORT/custom-ollama-gemma:latest"
docker push "$REGISTRY_NAME:$REGISTRY_PORT/agentic-architect-local:latest"

# 7. Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

echo "Done! Access TheArchitect at http://localhost:8080"
