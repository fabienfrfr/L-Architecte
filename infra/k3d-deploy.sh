#!/bin/bash
set -e

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="$CLUSTER_NAME-registry.localhost"
REGISTRY_PORT="5000"

# --- Arguments parsing ---
DEPLOY_WEB=false
for arg in "$@"; do
  if [ "$arg" == "--web" ] || [ "$arg" == "-w" ]; then
    DEPLOY_WEB=true
  fi
done

# --- Dependencies ---
if ! command -v k3d &> /dev/null; then
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

if ! command -v kubectl &> /dev/null; then
    K8S_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
    curl -LO "https://dl.k8s.io/release/${K8S_VERSION}/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
fi

# --- Cleanup ---
k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
k3d registry delete "$REGISTRY_NAME" 2>/dev/null || true
[ "$DEPLOY_WEB" = true ] && sudo sed -i '/thearchitect.dev/d' /etc/hosts 2>/dev/null || true

# --- Infrastructure ---
k3d registry create "$REGISTRY_NAME" --port "$REGISTRY_PORT"

if [ "$DEPLOY_WEB" = true ]; then
    k3d cluster create "$CLUSTER_NAME" \
        --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
        -p "80:80@loadbalancer" \
        -p "443:443@loadbalancer" \
        --wait
else
    k3d cluster create "$CLUSTER_NAME" \
        --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
        --k3s-arg "--disable=traefik@server:0" \
        --wait
fi

# --- Build and Push ---
docker build -t "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest" -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" "$PROJECT_ROOT"
docker build -t "localhost:$REGISTRY_PORT/agentic-architect-local:latest" -f "$PROJECT_ROOT/apps/architect/Dockerfile" "$PROJECT_ROOT"

docker push "localhost:$REGISTRY_PORT/custom-ollama-gemma:latest"
docker push "localhost:$REGISTRY_PORT/agentic-architect-local:latest"

# --- Deployment ---
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

if [ "$DEPLOY_WEB" = true ]; then
    kubectl apply -f "$PROJECT_ROOT/infra/k3s-ingress.yaml"
    sudo -- sh -c "echo '127.0.0.1 thearchitect.dev' >> /etc/hosts"
fi