#!/bin/bash
set -e

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME="agentic-cluster"
REGISTRY_NAME="k3d-$CLUSTER_NAME-registry.localhost"
REGISTRY_PORT="5000"

# --- Arguments parsing ---
DEPLOY_WEB=false
FORCE_RESET=false
for arg in "$@"; do
  if [ "$arg" == "--web" ] || [ "$arg" == "-w" ]; then DEPLOY_WEB=true; fi
  if [ "$arg" == "--reset" ]; then FORCE_RESET=true; fi
done

# --- Cleanup (Only if --reset is passed) ---
if [ "$FORCE_RESET" = true ]; then
    echo "Resetting infrastructure..."
    k3d cluster delete "$CLUSTER_NAME" 2>/dev/null || true
    k3d registry delete "$REGISTRY_NAME" 2>/dev/null || true
    [ "$DEPLOY_WEB" = true ] && sudo sed -i '/thearchitect.dev/d' /etc/hosts 2>/dev/null || true
fi

# --- Infrastructure ---
# Create registry if it doesn't exist
if ! k3d registry get "$REGISTRY_NAME" >/dev/null 2>&1; then
    k3d registry create "$REGISTRY_NAME" --port "$REGISTRY_PORT"
fi

# Create cluster if it doesn't exist
if ! k3d cluster get "$CLUSTER_NAME" >/dev/null 2>&1; then
    if [ "$DEPLOY_WEB" = true ]; then
        k3d cluster create "$CLUSTER_NAME" \
            --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
            -p "80:80@loadbalancer" \
            -p "443:443@loadbalancer" \
            --wait
        
        # Local DNS for Ingress
        if ! grep -q "thearchitect.dev" /etc/hosts; then
            echo "Adding thearchitect.dev to /etc/hosts..."
            sudo -- sh -c "echo '127.0.0.1 thearchitect.dev' >> /etc/hosts"
        fi
    else
        k3d cluster create "$CLUSTER_NAME" \
            --registry-use "$REGISTRY_NAME:$REGISTRY_PORT" \
            --k3s-arg "--disable=traefik@server:0" \
            --wait
    fi
fi

echo "Infrastructure is ready"