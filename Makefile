# --- Variables ---
NAMESPACE    = agentic-architect
CLUSTER_NAME = agentic-cluster
DOMAIN       = thearchitect.dev
USER         = ubuntu

DETECTED_MODE := $(shell [ -f /.dockerenv ] && echo "devcontainer" || [ "$$CI" = "true" ] && echo "ci" || echo "local")
MODE ?= $(DETECTED_MODE)

# --- K8s / K3D Specifics ---
K3S_DISK_ARGS = --k3s-arg "--kubelet-arg=eviction-hard=imagefs.available<1%,nodefs.available<1%@server:*" \
                --k3s-arg "--kubelet-arg=eviction-pressure-transition-period=0s@server:*"

K3S_NODE_ARGS = --k3s-arg "--kubelet-arg=image-pull-progress-deadline=2m@server:*"

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

setup-env: ## Initialize Python environment and create project files if missing
	@echo "📦 Preparing Python environment..."
	@uv venv .venv --python 3.13
	@export UV_LINK_MODE=copy && uv sync
	@echo "✅ Environment ready"

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
cluster: ## Create local k3d cluster + API fixed
	@if k3d cluster list | grep -q $(CLUSTER_NAME); then \
		echo "Cluster $(CLUSTER_NAME) exists..."; \
	else \
		k3d cluster create $(CLUSTER_NAME) \
			--port "8888:80@loadbalancer" \
			--api-port 6443 \
			$(K3S_DISK_ARGS) \
			$(K3S_NODE_ARGS) \
			--wait; \
		k3d kubeconfig get $(CLUSTER_NAME) > ~/.kube/config; \
	fi

wait: ## Run integration tests exactly as defined
	kubectl wait --for=condition=Ready pod -l app=ollama -n $(NAMESPACE) --timeout=600s
	kubectl wait --for=condition=Ready pod -l app=architect -n $(NAMESPACE) --timeout=300s

lint-fix: ## Répare automatiquement les erreurs de formatage/lint
	@uv run ruff check . --fix --exit-zero
	@uv run ruff format .

debug: ## Debug commands exactly as defined
	df -h
	kubectl get pods -A
	kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'
	kubectl logs -n $(NAMESPACE) -l app=architect --tail=100


# Port-forwarding
tunnels:
	@echo "🌐 Starting Tunnels..."
	@kubectl port-forward --address 127.0.0.1 svc/ollama 11434:11434 -n agentic-architect > /dev/null 2>&1 &
	@kubectl port-forward --address 127.0.0.1 svc/phoenix 6006:6006 -n agentic-architect > /dev/null 2>&1 &
	@kubectl port-forward --address 127.0.0.1 svc/phoenix 4317:4317 -n agentic-architect > /dev/null 2>&1 &
	@kubectl port-forward --address 127.0.0.1 svc/architect 8080:8080 -n agentic-architect > /dev/null 2>&1 &
	@kubectl port-forward --address 127.0.0.1 svc/architect 5678:5678 -n agentic-architect > /dev/null 2>&1 &
	@echo "⏳ Waiting for ports to open..."
	@timeout 30s bash -c 'until nc -z localhost 8080 && nc -z localhost 5678; do sleep 1; done' || (echo "❌ Tunnels failed to start" && exit 1)
	@echo "✅ Tunnels ready"

tunnels-stop:
	echo "Stopping tunnels..."
	@pkill -f "kubectl port-forward" || true

##@ Github CI

ci-test: wait
	@$(MAKE) tunnels
	@echo "🧪 Running CI Pipeline..."
	@APP_URL=http://localhost:8080 \
	 OLLAMA_URL=http://localhost:11434 \
	 PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317 \
	 DEBUG_PORT=5678 \
	 uv run pytest tests/ ; \
	 EXIT_CODE=$$? ; \
	 $(MAKE) tunnels-stop ; \
	 exit $$EXIT_CODE

ci-deep-clean: ## Deep cleanup for GitHub Runner disk space
	sudo rm -rf /usr/share/dotnet
	sudo rm -rf /usr/local/lib/android
	sudo rm -rf /opt/ghc
	sudo rm -rf /usr/local/share/boost
	sudo rm -rf /usr/local/lib/node_modules
	sudo docker image prune -af
	sudo rm -rf /usr/local/bin/aliyun
	sudo rm -rf /usr/local/bin/azcopy
	df -h

ci-tag-latest: ## Tag the images from build.json as latest and push
	@jq -r '.builds[] | .tag' build.json | xargs -I {} sh -c '\
		TAG_LATEST=$$(echo {} | cut -d: -f1):latest; \
		docker tag {} $$TAG_LATEST && docker push $$TAG_LATEST'

ci-fetch-kubeconfig: ## Fetch Kubeconfig from VPS and swap IP
	@mkdir -p ~/.ssh
	@ssh-keyscan -H $(DOMAIN) >> ~/.ssh/known_hosts
	@ssh $(USER)@$(DOMAIN) "sudo cat /etc/rancher/k3s/k3s.yaml" | \
		sed "s/127.0.0.1/$(DOMAIN)/g" > ~/.kube/config-vps
	@chmod 600 ~/.kube/config-vps

ci-deploy: ## Update image and restart deployment on VPS
	$(eval REPO_OWNER ?= $(shell echo $${GITHUB_REPOSITORY_OWNER}))
	@KUBECONFIG=~/.kube/config-vps kubectl set image deployment/architect \
		agentic-architect=ghcr.io/$(REPO_OWNER)/agentic-architect:latest -n $(NAMESPACE)
	@KUBECONFIG=~/.kube/config-vps kubectl rollout restart deployment -n $(NAMESPACE)

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
	-$(PULUMI_CMD) state delete --all --yes
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
	@# Remove legacy VS Code Snap environment injections that break devpod/devbox sessions
	-sed -i '/snap\/code/d' ~/.profile ~/.bashrc ~/.bash_aliases 2>/dev/null

nuke: clean ## ☢️  Wipe EVERYTHING (k3d + docker + volumes + process)
	@echo "Nuking system..."
	@k3d cluster delete --all || true
	@docker stop $$(docker ps -aq) 2>/dev/null || true
	@docker rm $$(docker ps -aq) 2>/dev/null || true
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@docker system prune -af --volumes
	@pgrep tmux > /dev/null && pkill -9 tmux || true
	@echo "✅ Reset complete. Clean slate for TheArchitect."

##@ DevPod in the box
setup-devpod:
	devpod provider add docker || true
	devpod provider use docker
	devpod delete agenticarchitect || true
	devpod up . --ide codium

#  Automatically collect all targets with descriptions for .PHONY
ALL_TARGETS := $(shell grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | cut -d: -f1)

.PHONY: $(ALL_TARGETS)