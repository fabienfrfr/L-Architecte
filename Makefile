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


install-tools: ## Install all binary dependencies (Skaffold, K3d, Kubectl, UV)
	@echo "Installing system tools..."
	# k3d
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
	@if ! command -v uv &> /dev/null; then \
		echo "Downloading and installing UV manually..."; \
		curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz -o uv.tar.gz && \
		tar -xzf uv.tar.gz && \
		sudo install -m 0755 ./uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv && \
		sudo install -m 0755 ./uv-x86_64-unknown-linux-gnu/uvx /usr/local/bin/uvx && \
		rm -rf uv.tar.gz ./uv-x86_64-unknown-linux-gnu; \
	fi
	@echo "All tools are installed."



setup-dev: .env ## Full development environment setup
	$(MAKE) clean
	$(MAKE) git-setup
	@echo "🚀 AgenticArchitect is setup!"

##@ Mapping
map: ## Export project structure to JSON
	uv run python3 libs/code_mapper.py --to-json

##@ Kubernetes (Local k3d)

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


##@ Storage & Cleanup
space: ## Show docker disk usage
	docker system df

nuke: ## WARNING: Completely wipe ALL local docker data
	@echo "⚠️  Wiping Docker..."
	docker system prune -a --volumes -f

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

##@ Deployment (VPS)
setup-vps: ## Install K3s and basic tools on the VPS
	ssh $(USER)@$(DOMAIN) "curl -sfL https://get.k3s.io | sh - && \
	sudo chmod 644 /etc/rancher/k3s/k3s.yaml && \
	sudo apt-get update && sudo apt-get install -y rsync"
	
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


clean-snap-pollution:
	@echo "Clean Snap... Only for Ubuntu!"
	@ls -la ~/snap/code/current/.local/bin/
	@rm -rf ~/snap/code/current/.local/bin/*


#  Automatically collect all targets with descriptions for .PHONY
ALL_TARGETS := $(shell grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | cut -d: -f1)

.PHONY: $(ALL_TARGETS)