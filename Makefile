# Project Variables
PYTHON = python3
PIP = pip
VENV = .venv
ACTIVATE = . $(VENV)/bin/activate

# Configuration
DOMAIN = thearchitect.dev
USER = ubuntu
PHOENIX_PORT = 6006

# Files
SCRIPT_MAPPER = libs/code_mapper.py

# Default target
.DEFAULT_GOAL := help

# url port
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

install: .env ## Create virtualenv and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "Installation complete."

##@ Mapping
map: ## Export project structure to JSON
	$(PYTHON) $(SCRIPT_MAPPER) --to-json

##@ Storage Management
space: ## Show docker disk usage
	docker system df

nuke: ## WARNING: Completely wipe ALL docker data (images, volumes, cache)
	@echo "⚠️  Wiping everything..."
	docker system prune -a --volumes -f

nuke-vps: ## WARNING: Completely wipe ALL docker data (images, volumes, cache)
	@echo "⚠️  Wiping everything..."
	ssh $(USER)@$(DOMAIN) "docker stop \$$(docker ps -q) 2>/dev/null || true && docker container prune -f"

##@ Development
run: ## Launch application in LOCAL mode
	$(ACTIVATE) && export PYTHONPATH=. && ENV=local python3 -m architect.main

test: ## Run pytest
	$(ACTIVATE) && export PYTHONPATH=. && pytest tests/

docker-run: ## Build and start local containers
	docker compose -f infra/services/docker-compose.yml up -d --build
	@docker ps


services-down: ## Stop ALL running containers and free RAM immediately
	@docker stop $$(docker ps -q) 2>/dev/null || true
	@docker container prune -f
	@docker network prune -f
	@docker ps

##@ Deployment
deploy: ## Deploy the project to OVH VPS
	@echo "📤 Uploading AgenticArchitect to $(DOMAIN)..."
	rsync -avz --exclude='.git' --exclude='.venv' ./ $(USER)@$(DOMAIN):~/AgenticArchitect
	ssh $(USER)@$(DOMAIN) "cd ~/AgenticArchitect && docker compose -f infra/services/docker-compose.yml --profile deploy up -d --build"

clean: ## Remove virtualenv and python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

git-setup: ## Configure Git inside the container using .env values
	@git config --global user.name "$$(grep GIT_USER_NAME .env | cut -d '=' -f2)"
	@git config --global user.email "$$(grep GIT_USER_EMAIL .env | cut -d '=' -f2)"
	@git config --global --add safe.directory /app

# Recursively set ownership and standard permissions
fix-permissions:
	sudo chown -R $(USER_NAME):$(GROUP_NAME) $(PROJECT_ROOT)
	find $(PROJECT_ROOT) -type d -exec chmod 755 {} +
	find $(PROJECT_ROOT) -type f -exec chmod 644 {} +

.PHONY: help install run test docker-run deploy clean services-down nuke nuke-vps space git-setup fix-permissions map .env