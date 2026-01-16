#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="$CLUSTER_NAME-registry.localhost"  # Internal registry name
REGISTRY_PORT="5000"

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 1. Cleanup existing cluster and registry
echo "Cleaning up existing cluster and registry..."
k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
k3d registry delete "$REGISTRY_NAME" 2>/dev/null || true
sudo sed -i '/thearchitect.dev/d' /etc/hosts 2>/dev/null || true

# 2. Create local registry (accessible via localhost:5000)
echo "Creating local registry..."
k3d registry create "$REGISTRY_NAME" --port "$REGISTRY_PORT"

# 3. Create cluster with registry integration
echo "Creating Kubernetes cluster..."
k3d cluster create "$CLUSTER_NAME" \
    --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
    -p "8080:80@loadbalancer" \
    --wait

# 4. Build and push images (using localhost for your PC)
echo "Building Docker images..."
docker build -t "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest" -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"
docker build -t "localhost:$REGISTRY_PORT/agentic-architect-local:latest" -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

echo "Pushing images to registry..."
docker push "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest"
docker push "localhost:$REGISTRY_PORT/agentic-architect-local:latest"

# 5. Deploy Kubernetes manifests (K8s will use internal DNS name)
echo "Deploying Kubernetes manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

# 6. Add thearchitect.dev to /etc/hosts for local access
echo "Configuring local access..."
sudo -- sh -c "echo '127.0.0.1 thearchitect.dev' >> /etc/hosts"

echo "✅ Done! Access TheArchitect at http://thearchitect.dev"
