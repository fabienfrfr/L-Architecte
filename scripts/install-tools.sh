#!/bin/bash

# ==============================================================================
# AgenticArchitect - Unified Setup Script
# Version: 1.1.0
# Description: Handles core engine installation (Docker/K3s) and Devbox.
# ==============================================================================

set -e # Exit on error
set -u # Exit on unset variables

# --- Configuration ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helpers ---
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

show_help() {
    echo "Usage: $0 [target]"
    echo ""
    echo "Targets:"
    echo "  local    Install Docker and Devbox (PC/CI)"
    echo "  vps      Install K3s only (Production Node)"
    echo ""
    exit 1
}

# --- Installation Logic ---

install_devbox() {
    if ! command -v devbox &> /dev/null; then
        log_info "Installing Devbox (Nix-based toolchain)..."
        # Devbox install script handles sudo internally if needed
        curl -fsSL https://get.jetpack.io/devbox | bash
    else
        log_info "Devbox is already installed."
    fi
}

install_docker() {
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker Engine..."
        curl -fsSL https://get.docker.com | sh
        # Use sudo for group modification
        sudo usermod -aG docker "$USER"
        log_warn "You might need to log out and back in for docker group changes to take effect."
    else
        log_info "Docker is already installed."
    fi
}

install_k3s() {
    if ! command -v k3s &> /dev/null; then
        log_info "Installing K3s (Lightweight Kubernetes)..."
        # K3s installation requires root
        curl -sfL https://get.k3s.io | sh -
    else
        log_info "K3s is already installed."
    fi
}

# --- Execution ---

if [ $# -eq 0 ]; then
    show_help
fi

case "$1" in
    local|ci)
        log_info "Initializing LOCAL/CI environment..."
        install_docker
        install_devbox
        log_success "Core engines ready. Tools will be auto-installed by Devbox on first use."
        ;;
    
    vps)
        log_info "Initializing VPS Production Node..."
        install_k3s
        log_success "VPS setup complete. Minimal footprint maintained."
        ;;

    *)
        show_help
        ;;
esac