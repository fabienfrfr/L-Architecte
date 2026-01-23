# --- Variables ---
NAMESPACE    = agentic-architect
CLUSTER_NAME = agentic-cluster
DOMAIN       = thearchitect.dev
USER         = ubuntu

DETECTED_MODE := $(shell [ -f /.dockerenv ] && echo "devcontainer" || [ "$$CI" = "true" ] && echo "ci" || echo "local")
MODE ?= $(DETECTED_MODE)

# Infrastructure
INFRA_DIR    = infra
PULUMI_ENV   = PULUMI_CONFIG_PASSPHRASE=""
PULUMI_CMD   = $(PULUMI_ENV) uv run pulumi --cwd $(INFRA_DIR)

# --- Internal K8s DNS / Ports ---
OLLAMA_URL                 = http://ollama:11434
PHOENIX_URL                = http://phoenix:6006
PHOENIX_COLLECTOR_ENDPOINT = http://phoenix:4317

.DEFAULT_GOAL := help

# Cloud Provider (api.ovh.com/create-app/ + https://eu.api.ovh.com/createToken/?GET=/vps/*)
OVH_ENDPOINT=ovh-eu
OVH_APPLICATION_KEY=.
OVH_APPLICATION_SECRET=.
OVH_CONSUMER_KEY=.

##@ General
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

##@ Setup & Installation
install: ## Install system binaries
	@echo "🛠️ Target mode: $(MODE)"
	@bash scripts/install-tools.sh $(MODE)

.env: ## Create default environment file
	@test -f .env || (echo "PYTHONPATH=.\nENV=test\nOLLAMA_URL=$(OLLAMA_URL)\nDOMAIN=$(DOMAIN)\nPHOENIX_URL=$(PHOENIX_URL)" > .env && echo "✅ .env created")

code-map: ## Export project structure to JSON
	uv run python3 libs/code_mapper.py --to-json

vps-auth: ## Generate SSH key if missing and copy it to VPS
	@if [ ! -f ~/.ssh/id_rsa ]; then \
		echo "Generating new SSH key..."; \
		ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""; \
	fi
	@ssh-copy-id ubuntu@thearchitect.dev

##@ Kubernetes
cluster: ## Create local k3d cluster with port forwarding
	@if k3d cluster list | grep -q $(CLUSTER_NAME); then \
		echo "Cluster $(CLUSTER_NAME) exists..."; \
	else \
		k3d cluster create $(CLUSTER_NAME) \
			--port "8888:80@loadbalancer" \
			--wait; \
	fi

##@ Release
release: ## 🚢 Build and Push images to GHCR
	@chmod +x scripts/release-ghcr.sh
	./scripts/release-ghcr.sh

##@ (Pulumi) Infrastructure & Deployment

infra-auth: ## Setup Pulumi secrets for OVH API (Interactive)
	@echo "🔐 Configuring OVH API Secrets for Pulumi..."
	@read -p "Enter OVH Application Key: " ak; \
	 $(PULUMI_CMD) config set ovh:applicationKey $$ak --secret
	@read -p "Enter OVH Application Secret: " as; \
	 $(PULUMI_CMD) config set ovh:applicationSecret $$as --secret
	@read -p "Enter OVH Consumer Key: " ck; \
	 $(PULUMI_CMD) config set ovh:consumerKey $$ck --secret
	@$(PULUMI_CMD) config set ovh:endpoint $(OVH_ENDPOINT)
	@echo "✅ Pulumi secrets configured in $(INFRA_DIR)/Pulumi.dev.yaml"

infra-reinstall: ## 🚀 FULL REINSTALL: Trigger OVH Reinstall + System + App
	$(PULUMI_CMD) up \
		-c setup_infra=true \
		-c setup_system=true \
		-c deploy_app=true \
		-c force_reinstall=true \
		--yes

reset-pulumi: ## ☢️ FACTORY RESET: Wipe Pulumi state and re-init
	@echo "⚠️ Deleting Pulumi stack $(STACK_NAME)..."
	$(PULUMI_CMD) stack rm $(STACK_NAME) --force --yes || true
	$(PULUMI_CMD) stack init $(STACK_NAME)
	@echo "👉 Now run 'make infra-auth' to re-inject your secrets."


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


##@ DevPod in the box
setup-devpod:
	devpod provider add docker || true
	devpod provider use docker
	devpod delete agenticarchitect || true
	devpod up . --ide codium

#  Automatically collect all targets with descriptions for .PHONY
ALL_TARGETS := $(shell grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | cut -d: -f1)

.PHONY: $(ALL_TARGETS)