#!/bin/bash
# ==============================================================================
# Infrastructure Setup for AgenticArchitect (Local Sideloading Mode)
# ==============================================================================
set -e

CLUSTER_NAME="agentic-cluster"
CONFIG_FILE="infra/k3d/config.yaml"

echo "🚀 Starting infrastructure initialization..."

if [ "$1" == "--reset" ]; then
    echo "♻️ Resetting cluster..."
    k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
fi

# Create K3D cluster using the CONFIG FILE
if ! k3d cluster get "$CLUSTER_NAME" >/dev/null 2>&1; then
    echo "🏗️ Creating cluster $CLUSTER_NAME from $CONFIG_FILE..."
    k3d cluster create --config "$CONFIG_FILE"
else
    echo "ℹ️ Cluster $CLUSTER_NAME already exists."
fi

echo "✅ Infrastructure is ready for Skaffold (Sideloading mode)."