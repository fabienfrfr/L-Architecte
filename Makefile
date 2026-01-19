# --- Variables ---
NAMESPACE    = agentic-architect
CLUSTER_NAME = agentic-cluster
DOMAIN       = thearchitect.dev
USER         = ubuntu

DETECTED_MODE := $(shell [ -f /.dockerenv ] && echo "devcontainer" || [ "$$CI" = "true" ] && echo "ci" || echo "local")
MODE ?= $(DETECTED_MODE)

# --- Internal K8s DNS / Ports ---
OLLAMA_URL                 = http://ollama:11434
PHOENIX_URL                = http://phoenix:6006
PHOENIX_COLLECTOR_ENDPOINT = http://phoenix:4317

.DEFAULT_GOAL := help

##@ General
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

##@ Setup & Installation
install: ## Install system binaries
	@echo "🛠️ Target mode: $(MODE)"
	@bash scripts/install-tools.sh $(MODE)

setup-dev: .env ## Sync dependencies and prepare project
	uv sync
	@git config --global --add safe.directory $(shell pwd)
	@echo "🚀 AgenticArchitect is ready!"

.env: ## Create default environment file
	@test -f .env || (echo "PYTHONPATH=.\nENV=test\nOLLAMA_URL=$(OLLAMA_URL)\nDOMAIN=$(DOMAIN)\nPHOENIX_URL=$(PHOENIX_URL)" > .env && echo "✅ .env created")

##@ Development (Local)
run: ## Launch application using UV (Auto-venv)
	export PYTHONPATH=. && ENV=local uv run python3 -m architect.main

test: ## Run pytest using UV
	export PYTHONPATH=. && uv run pytest tests/

map: ## Export project structure to JSON
	uv run python3 libs/code_mapper.py --to-json

##@ Kubernetes (k3d/k3s)
k-cluster: ## Create local k3d cluster with port forwarding
	k3d cluster create $(CLUSTER_NAME) --port "8080:80@loadbalancer"

k-status: ## Check status of local/current cluster
	kubectl get pods,svc,pvc -n $(NAMESPACE) -o wide

k-logs: ## Follow logs for the main agent
	kubectl logs -l app=architect -n $(NAMESPACE) -f

##@ Deployment (VPS)
vps-bootstrap: ## One-click K3s installation on OVH VPS
	ssh $(USER)@$(DOMAIN) 'bash -s' < scripts/install.sh vps

deploy: map ## Build map and push to production VPS
	@echo "📤 Uploading files to $(DOMAIN)..."
	rsync -avz --exclude={'.git','.venv','__pycache__','.pytest_cache'} ./ $(USER)@$(DOMAIN):~/AgenticArchitect
	ssh $(USER)@$(DOMAIN) "kubectl apply -f ~/AgenticArchitect/$(K8S_STACK)"

##@ Maintenance
clean: ## Remove python caches and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .venv .ruff_cache .mypy_cache

nuke: clean ## ☢️  Wipe EVERYTHING (k3d + docker)
	@echo "Nuking system..."
	@k3d cluster delete --all || true
	@docker stop $$(docker ps -aq) 2>/dev/null || true
	@docker system prune -af --volumes
	@echo "✅ Reset complete."

#  Automatically collect all targets with descriptions for .PHONY
ALL_TARGETS := $(shell grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | cut -d: -f1)

.PHONY: $(ALL_TARGETS)