#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="k3d-$CLUSTER_NAME-registry"  # Internal DNS name
REGISTRY_PORT="5000"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Cleanup
k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
k3d registry delete "$REGISTRY_NAME" 2>/dev/null || true

# 3. Create registry and cluster
echo "Creating registry..."
k3d registry create "$REGISTRY_NAME" --port "$REGISTRY_PORT"

echo "Creating cluster..."
k3d cluster create "$CLUSTER_NAME" \
    --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
    -p "8080:80@loadbalancer" \
    --wait

# 4. Build and push images (using localhost for your PC)
echo "Building and pushing images..."
docker build -t "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest" -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"
docker build -t "localhost:$REGISTRY_PORT/agentic-architect-local:latest" -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

docker push "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest"
docker push "localhost:$REGISTRY_PORT/agentic-architect-local:latest"

# 5. Apply manifests (K8s will pull using internal DNS)
echo "Applying manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

# 6. Add thearchitect.dev to /etc/hosts (for local testing)
echo "Adding thearchitect.dev to /etc/hosts..."
sudo -- sh -c "echo '127.0.0.1 thearchitect.dev' >> /etc/hosts"

echo "Done! Access TheArchitect at http://thearchitect.dev"
