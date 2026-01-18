#!/bin/bash

# ==============================================================================
# AgenticArchitect - Multi-purpose Installation Script
# Supports: local, devcontainer, vps
# ==============================================================================

set -e # Exit on error
set -u # Exit on unset variables

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# --- Shared Installation Logic ---

install_uv() {
    if ! command -v uv &> /dev/null; then
        log_info "Installing UV (Python toolchain)..."
        curl -LsSf https://astral-sh/uv/install.sh | sh
    else
        log_info "UV is already installed."
    fi
}

install_k8s_tools() {
    log_info "Installing Kubernetes CLI tools (Skaffold & Kubectl)..."
    # Skaffold
    curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
    sudo install skaffold /usr/local/bin/ && rm skaffold
    
    # Kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
}

install_vps_essentials() {
    log_info "Installing VPS essentials (K3s, rsync)..."
    sudo apt-get update && sudo apt-get install -y rsync curl
    curl -sfL https://get.k3s.io | sh -
}

# --- Main Execution Paths ---

show_help() {
    echo "Usage: $0 [target]"
    echo "Targets:"
    echo "  local          Install everything for a full local dev machine"
    echo "  devcontainer   Install only tools needed inside the DevContainer (Skaffold, UV)"
    echo "  vps            Install K3s and production essentials"
    exit 1
}

if [ $# -eq 0 ]; then
    show_help
fi

case "$1" in
    local)
        log_info "Starting FULL LOCAL installation..."
        install_uv
        install_k8s_tools
        log_success "Local environment ready."
        ;;
    devcontainer)
        log_info "Starting DEVCONTAINER setup..."
        # In DevContainer, we only need the management tools
        install_uv
        install_k8s_tools
        log_success "DevContainer tools installed."
        ;;
    vps)
        log_info "Starting VPS production setup..."
        install_vps_essentials
        log_success "VPS is now a K3s node."
        ;;
    *)
        show_help
        ;;
esac