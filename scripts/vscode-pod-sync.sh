#!/bin/bash

# ==============================================================================
# Description: Automatically detects the Architect Pod and attaches VS Code.
# ==============================================================================

# Configuration
APP_LABEL="app=architect"
NAMESPACE="default"
CLUSTER_NAME="k3d-agentic-cluster"
CONTAINER_NAME="architect"
WORKSPACE_DIR="/workspaces/AgenticArchitect"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "⏳ [TheArchitect] Waiting for Skaffold to deploy the Pod ($APP_LABEL)..."

# Wait for the Pod to be in 'Running' state with a timeout
count=0
until kubectl get pods -l "$APP_LABEL" -n "$NAMESPACE" --field-selector=status.phase=Running | grep -q "Running"; do
    ((count++))
    if [ $count -gt $MAX_RETRIES ]; then
        echo "❌ [Error] Timeout reached: Pod not found or not running after $((MAX_RETRIES * RETRY_INTERVAL))s."
        exit 1
    fi
    sleep $RETRY_INTERVAL
done

# Extract the exact Pod name
POD_NAME=$(kubectl get pods -l "$APP_LABEL" -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "❌ [Error] Failed to retrieve Pod name."
    exit 1
fi

echo "✅ [Success] Pod found: $POD_NAME"
echo "🚀 [TheArchitect] Opening remote VS Code session into Pod..."

# Construct the VS Code Remote URI for Kubernetes
# Format: vscode-remote://kubernetes-container+cluster=<cluster>+namespace=<ns>+pod=<pod>+container=<container>/<path>
REMOTE_URI="vscode-remote://kubernetes-container+cluster=${CLUSTER_NAME}+namespace=${NAMESPACE}+pod=${POD_NAME}+container=${CONTAINER_NAME}${WORKSPACE_DIR}"

code --folder-uri="$REMOTE_URI"