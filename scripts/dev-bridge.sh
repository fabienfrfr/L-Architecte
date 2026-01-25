#!/bin/bash
set -e

CLUSTER_NAME="agentic-cluster"
LB_CONTAINER="k3d-${CLUSTER_NAME}-serverlb"
KUBE_CONFIG="$HOME/.kube/config"

mkdir -p "$HOME/.kube"

echo "🔗 Detecting K3d LoadBalancer port..."
HOST_PORT=$(docker inspect "$LB_CONTAINER" --format='{{(index (index .NetworkSettings.Ports "6443/tcp") 0).HostPort}}')

echo "🚀 Patching Kubeconfig: host.docker.internal:$HOST_PORT"
k3d kubeconfig get "$CLUSTER_NAME" > "$KUBE_CONFIG"

sed -i "s/0.0.0.0:6443/host.docker.internal:$HOST_PORT/g" "$KUBE_CONFIG"

echo "✅ Bridge established."