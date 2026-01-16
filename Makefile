# Project Variables
PYTHON = python3
PIP = pip
VENV = .venv
ACTIVATE = . $(VENV)/bin/activate

# Configuration
DOMAIN = thearchitect.dev
USER = ubuntu
PHOENIX_PORT = 6006
NAMESPACE = agentic-architect
CLUSTER_NAME = agentic-cluster

# Files
SCRIPT_MAPPER = libs/code_mapper.py
K8S_STACK = infra/k3s-stack.yaml

# Default target
.DEFAULT_GOAL := help

# URL and Ports (Internal K8s DNS)
OLLAMA_URL=http://ollama:11434
PHOENIX_URL=http://phoenix:6006
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317

# Directory and User Variables
USER_NAME := $(shell whoami)
GROUP_NAME := $(shell id -gn)
PROJECT_ROOT := $(shell pwd)

##@ Help
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

##@ Setup
.env: ## Create default .env file ONLY if it doesn't exist
	@if [ ! -f .env ]; then \
		echo "PYTHONPATH=." > .env; \
		echo "ENV=test" >> .env; \
		echo "OLLAMA_URL=$(OLLAMA_URL)" >> .env; \
		echo "PHOENIX_URL=$(PHOENIX_URL)" >> .env; \
		echo "NICEGUI_NATIVE=False" >> .env; \
		echo "DOMAIN=$(DOMAIN)" >> .env; \
		echo "USER=$(USER)" >> .env; \
		echo "PHOENIX_PORT=$(PHOENIX_PORT)" >> .env; \
		echo "PHOENIX_COLLECTOR_ENDPOINT=$(PHOENIX_COLLECTOR_ENDPOINT)" >> .env; \
		echo "GIT_USER_NAME=" >> .env; \
		echo "GIT_USER_EMAIL=" >> .env; \
		echo "✅ .env file created."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi

# --- Configuration ---
SHELL := /bin/bash
PROJECT_NAME := agentic-architect

.PHONY: help install-tools setup-infra dev clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-tools: ## Install all binary dependencies (Skaffold, K3d, Kubectl, UV)
	@echo "Installing system tools..."
	# K3D
	@if ! command -v k3d &> /dev/null; then curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash; fi
	# Kubectl
	@if ! command -v kubectl &> /dev/null; then \
		curl -LO "https://dl.k8s.io/release/$$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
		sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl; \
	fi
	# Skaffold
	@if ! command -v skaffold &> /dev/null; then \
		curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
		sudo install skaffold /usr/local/bin/ && rm skaffold; \
	fi
	# UV (Fast Python toolchain)
	@if ! command -v uv &> /dev/null; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
	@echo "All tools are installed."

setup-infra: install-tools ## Create the K3d cluster and registry
	bash infra/k3d-deploy.sh --reset
	k3d kubeconfig merge agentic-cluster --switch-context

dev: ## Start the Skaffold development loop
	@echo "Starting AgenticArchitect development loop..."
	skaffold dev --cleanup=false

clean: ## Destroy the cluster and clean local artifacts
	k3d cluster delete agentic-cluster
	k3d registry delete agentic-registry.localhost

setup-dev: .env ## Full development environment setup
	$(MAKE) clean
	$(PIP) install -r apps/architect/requirements.txt
	$(MAKE) git-setup
	$(PYTHON) -m pytest --collect-only
	@echo "🚀 AgenticArchitect is ready!"

##@ Mapping
map: ## Export project structure to JSON
	$(PYTHON) $(SCRIPT_MAPPER) --to-json

##@ Kubernetes (Local k3d)
k-up: ## Deploy infrastructure to k3d cluster (Build + Deploy)
	bash infra/k3d-deploy.sh

k-status: ## Show all pods, services and nodes in the namespace
	@echo "📊 Cluster Status:"
	kubectl get pods,svc,pvc -n $(NAMESPACE) -o wide

k-debug: ## Detailed debug of the pods (events + description)
	@echo "🔍 Debugging Ollama..."
	kubectl describe pod -l app=ollama -n $(NAMESPACE)
	@echo "📜 Last logs:"
	kubectl logs -l app=ollama -n $(NAMESPACE) --tail=20

k-test: ## Run pytest INSIDE the architect pod in k3d
	kubectl exec -n $(NAMESPACE) deployments/architect -- pytest tests/

k-models: ## List models available in the k3d ollama instance
	kubectl exec -n $(NAMESPACE) deployments/ollama -- ollama list

k-nuke: ## WARNING: Completely destroy the k3d cluster and registry
	@echo "🔥 Destroying K3d Infrastructure..."
	k3d cluster delete $(CLUSTER_NAME) || true
	k3d registry delete k3d-registry.localhost || true

##@ Storage & Cleanup
space: ## Show docker disk usage
	docker system df

nuke: ## WARNING: Completely wipe ALL local docker data
	@echo "⚠️  Wiping Docker..."
	docker system prune -a --volumes -f

nuke-vps: ## WARNING: Completely wipe ALL K8s resources on VPS
	@echo "⚠️  Wiping VPS Namespace..."
	ssh $(USER)@$(DOMAIN) "kubectl delete namespace $(NAMESPACE) || true"

clean: ## Remove virtualenv and python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache .venv

fix-permissions: ## Set ownership and standard permissions
	sudo chown -R $(USER_NAME):$(GROUP_NAME) $(PROJECT_ROOT)
	find $(PROJECT_ROOT) -type d -exec chmod 755 {} +
	find $(PROJECT_ROOT) -type f -exec chmod 644 {} +

##@ Development (Local)
run: ## Launch application in LOCAL mode (Host machine)
	$(ACTIVATE) && export PYTHONPATH=. && ENV=local python3 -m architect.main

test: ## Run pytest locally
	$(ACTIVATE) && export PYTHONPATH=. && pytest tests/


services-down: ## Stop ALL running containers and free RAM immediately
	@docker stop $$(docker ps -q) 2>/dev/null || true
	@docker container prune -f
	@docker network prune -f
	@docker ps

pods-down: ## Stop local k3d cluster to free RAM
	k3d cluster stop $(CLUSTER_NAME)

##@ Deployment (VPS)
deploy: ## Deploy the project to OVH VPS using K3s
	@echo "📤 Uploading AgenticArchitect to $(DOMAIN)..."
	rsync -avz --exclude='.git' --exclude='.venv' ./ $(USER)@$(DOMAIN):~/AgenticArchitect
	@echo "🚀 Applying K8s Manifests on VPS..."
	ssh $(USER)@$(DOMAIN) "kubectl apply -f ~/AgenticArchitect/$(K8S_STACK)"

vps-status: ## Check status of the production cluster on VPS
	ssh $(USER)@$(DOMAIN) "kubectl get pods -n $(NAMESPACE) -o wide"

git-setup: ## Configure Git inside the container using .env values
	@git config --global user.name "$$(grep GIT_USER_NAME .env | cut -d '=' -f2)"
	@git config --global user.email "$$(grep GIT_USER_EMAIL .env | cut -d '=' -f2)"
	@git config --global --add safe.directory /app



#  Automatically collect all targets with descriptions for .PHONY
ALL_TARGETS := $(shell grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | cut -d: -f1)

.PHONY: $(ALL_TARGETS)