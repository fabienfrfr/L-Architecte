#!/bin/bash

# ==============================================================================
# AgenticArchitect - Unified Setup Script
# Description: Handles core engine installation.
# ==============================================================================

set -e 
set -u 

# --- Configuration ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' 

# --- Helpers ---
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

show_help() {
    echo "Usage: $0 [target]"
    echo ""
    echo "Targets:"
    echo "  local    Install Docker, Devbox AND DevPod (Your IdeaPad)"
    echo "  ci       Install Docker and Devbox ONLY (GitHub Actions)"
    echo "  vps      Install K3s only (Production Node)"
    exit 1
}

# --- Installation Logic ---

install_devbox() {
    if ! command -v devbox &> /dev/null; then
        log_info "Installing Devbox..."
        curl -fsSL https://get.jetpack.io/devbox | bash
    else
        log_info "Devbox is already installed."
    fi
}

install_devpod() {
    if ! command -v devpod &> /dev/null; then
        log_info "Installing DevPod CLI (Local Desktop Only)..."
        curl -L https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64 -o devpod
        sudo install -c -m 0755 devpod /usr/local/bin && rm devpod
        devpod provider add docker
    else
        log_info "DevPod is already installed."
    fi
}

install_docker() {
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker Engine..."
        curl -fsSL https://get.docker.com | sh
        # Check if we are in a non-interactive shell (CI) to avoid usermod issues
        if [ -t 0 ]; then
            sudo usermod -aG docker "$USER"
            log_warn "Log out/in for docker group changes."
        fi
    else
        log_info "Docker is already installed."
    fi
}

install_k3s() {
    if ! command -v k3s &> /dev/null; then
        log_info "Installing K3s with SAN for $K3S_TLS_SAN..."
        curl -sfL https://get.k3s.io | sh -s - server \
            --write-kubeconfig-mode 644 \
            ${K3S_TLS_SAN:+--tls-san="$K3S_TLS_SAN"}
    else
        log_info "K3s is already installed."
    fi
}

# --- Execution ---

if [ $# -eq 0 ]; then
    show_help
fi

case "$1" in
    local)
        log_info "Initializing LOCAL Desktop environment..."
        install_docker
        install_devbox
        install_devpod
        log_success "Local environment ready. Use 'devpod up .' to start."
        ;;
    
    ci)
        log_info "Initializing CI environment (No DevPod)..."
        install_docker
        install_devbox
        log_success "CI environment ready. Running directly via Devbox."
        ;;
    
    vps)
        log_info "Initializing VPS Production Node..."
        install_docker
        install_k3s
        log_success "VPS setup complete."
        ;;

    *)
        show_help
        ;;
esac