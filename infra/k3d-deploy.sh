#!/bin/bash
# --- Standard Deployment Script for AgenticArchitect (Local & CI) ---
set -e

# Détermination de la racine du projet (un niveau au-dessus de infra/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
ARCHITECT_IMAGE="agentic-architect-local:latest"
OLLAMA_IMAGE="custom-ollama-gemma:latest"

echo "🛠️ Project Root: $PROJECT_ROOT"

# 1. Installation de k3d si manquant
if ! command -v k3d &> /dev/null; then
    echo "📥 Installing k3d..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

# 2. Création du cluster (propre et sans conflit)
if ! k3d cluster get $CLUSTER_NAME &>/dev/null; then
    echo "🏗️ Creating cluster $CLUSTER_NAME..."
    k3d cluster create $CLUSTER_NAME \
        --k3s-arg '--disable=traefik@server:*' \
        -p "8080:80@loadbalancer" \
        --wait
fi

# 3. Build des images (Le cœur de la performance)
echo "📦 Building $ARCHITECT_IMAGE..."
docker build -t $ARCHITECT_IMAGE \
    -f "$PROJECT_ROOT/apps/architect/Dockerfile" \
    "$PROJECT_ROOT"

echo "📦 Building $OLLAMA_IMAGE (This includes Gemma 3:270m)..."
docker build -t $OLLAMA_IMAGE \
    -f "$PROJECT_ROOT/infra/Ollama.Dockerfile" \
    "$PROJECT_ROOT"

# 4. Importation dans le cluster (Crucial pour k3d)
echo "📥 Importing images to k3d..."
k3d image import $ARCHITECT_IMAGE -c $CLUSTER_NAME
k3d image import $OLLAMA_IMAGE -c $CLUSTER_NAME

# 5. Déploiement des Manifestes
echo "⎈ Applying manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k3s-stack.yaml"

echo "✅ Deployment successful! Your infrastructure is ready."