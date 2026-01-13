#!/bin/bash
# --- Standard Deployment Script for AgenticArchitect (Local & CI) ---
set -e

CLUSTER_NAME="agentic-cluster"
IMAGE_NAME="agentic-architect-local:latest"

echo "🛠️ Checking prerequisites..."

# 1. Install k3d if missing
if ! command -v k3d &> /dev/null; then
    echo "📥 k3d not found. Installing..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
else
    echo "✅ k3d is already installed."
fi

# 2. Create cluster if it doesn't exist
if ! k3d cluster get $CLUSTER_NAME &>/dev/null; then
    echo "🏗️ Creating k3d cluster: $CLUSTER_NAME..."
    k3d cluster create $CLUSTER_NAME \
        --k3s-arg '--disable=traefik@server:*' \
        -p "8080:80@loadbalancer" \
        --wait
else
    echo "✅ Cluster $CLUSTER_NAME already exists."
fi

# 3. Build and Import Image
echo "📦 Building and importing $IMAGE_NAME..."
docker build -t $IMAGE_NAME .
k3d image import $IMAGE_NAME -c $CLUSTER_NAME

# 4. Apply Kubernetes Stack
echo "⎈ Applying manifests from infra/k3s-stack.yaml..."
kubectl apply -f infra/k3s-stack.yaml

echo "✅ AgenticArchitect (TheArchitect) deployed successfully!"