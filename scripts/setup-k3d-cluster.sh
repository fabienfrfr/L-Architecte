#!/bin/bash
# ==============================================================================
# Infrastructure Setup for AgenticArchitect (Local Sideloading Mode)
# ==============================================================================
set -e

CLUSTER_NAME="agentic-cluster"

echo "🚀 Starting infrastructure initialization..."

if [ "$1" == "--reset" ]; then
    echo "♻️ Resetting cluster..."
    k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
fi

# Create K3D cluster
if ! k3d cluster get "$CLUSTER_NAME" >/dev/null 2>&1; then
    echo "🏗️ Creating cluster $CLUSTER_NAME..."
    k3d cluster create "$CLUSTER_NAME" \
        --k3s-arg "--disable=traefik@server:0" \
        --wait
fi

echo "✅ Infrastructure is ready for Skaffold (Sideloading mode)."