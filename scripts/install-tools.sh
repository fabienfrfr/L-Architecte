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

install_k3d() {
    if ! command -v k3d &> /dev/null; then
        log_info "Installing k3d (Local Cluster Provider)..."
        curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    else
        log_info "k3d is already installed."
    fi
}

install_helm() {
    if ! command -v helm &> /dev/null; then
        log_info "Installing Helm (Kubernetes Package Manager)..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    else
        log_info "Helm is already installed."
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


install_devbox() {
    if ! command -v devbox &> /dev/null; then
        log_info "Installing Devbox (Nix-based environments)..."
        if ! command -v nix &> /dev/null; then
            log_info "Nix not found. Installing Nix multi-user..."
            curl -L https://nixos.org/nix/install | sh -s -- --daemon
        fi
        curl -fsSL https://get.jetpack.io/devbox | bash
    else
        log_info "Devbox is already installed."
    fi
}

install_devpod() {
    if ! command -v devpod &> /dev/null; then
        log_info "Installing DevPod CLI..."
        curl -L https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64 -o devpod
        sudo install -c -m 0755 devpod /usr/local/bin && rm devpod
    else
        log_info "DevPod is already installed."
    fi
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
        install_devbox
        install_devpod
        install_k3d
        install_k8s_tools
        install_helm
        log_success "Local environment ready."
        ;;
    ci)
        log_info "Starting CI installation..."
        install_uv
        install_k3d
        install_k8s_tools
        install_helm
        log_success "CI environment ready."
        ;;
    devcontainer)
        log_info "Starting DEVCONTAINER setup..."
        install_uv
        install_k8s_tools
        install_helm
        log_success "DevContainer tools installed."
        ;;
    vps)
        log_info "Starting VPS production setup..."
        install_vps_essentials
        install_helm
        log_success "VPS is now a K3s node with Helm."
        ;;
    *)
        show_help
        ;;
esac