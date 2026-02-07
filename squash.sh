#!/bin/bash
# Clean, English comments for automated history restructuring

# 1. Safety check
git checkout -b history-rebuilt-32

# 2. Reset to the first commit (keeping all changes staged)
git reset --soft d0bd2e4

smart_commit() {
    local message=$1
    shift
    local patterns=$@
    for p in $patterns; do git add "$p" 2>/dev/null; done
    if ! git diff --cached --quiet; then
        git commit -m "$message"
    fi
}

# --- THE 32 STEPS SEQUENCE ---

# PHASE 1: FOUNDATIONS & SPECS (1-4)
smart_commit "feat: project skeleton and functional specifications" "README.md" "LICENSE" "docs/functional_specs"
smart_commit "docs: add initial architecture diagrams and swimlanes" "docs/diagrams" "*.png"
smart_commit "feat: add basic project structure and code mapper" "scripts/code_mapper" "Makefile"
smart_commit "docs: define ADRs for technology stack" "docs/adr"

# PHASE 2: INFRASTRUCTURE & OPS (5-12)
smart_commit "infra: setup OVH VPS management with Terraform" "terraform/"
smart_commit "infra: implement Pulumi IaC for cloud resources" "pulumi/"
smart_commit "infra: add helm management and k8s config" "k8s/helm" "charts/"
smart_commit "k8s: setup k3s cluster and local k3d registry" "scripts/k3s*" "scripts/setup-k3d*"
smart_commit "ci: bootstrap github actions and basic pipelines" ".github/workflows/main.yml"
smart_commit "ci: add mirroring to codeberg" ".github/workflows/mirror.yml"
smart_commit "dev: introduce devbox for environment reproducibility" "devbox.json" "devbox.lock"
smart_commit "dev: configure devpod and devcontainer for vscodium" ".devcontainer/" "devpod.yaml"

# PHASE 3: CORE ARCHITECTURE (13-20)
smart_commit "arch: structure apps project toward DDD" "apps/domain" "apps/architect"
smart_commit "feat: implement basic NiceGUI frontend" "apps/ui" "*nicegui*"
smart_commit "refactor: move to full-stack python (NiceGUI/FastAPI)" "apps/main.py"
smart_commit "feat: add observability with Arize Phoenix" "*phoenix*"
smart_commit "feat: add LLMops tracking with Langfuse" "*langfuse*"
smart_commit "feat: integrate Ollama for local model execution" "*ollama*" "Ollama.Dockerfile"
smart_commit "feat: add ArangoDB graph database support" "*arango*"
smart_commit "feat: add FastEmbed for semantic entity extraction" "*fastembed*"

# PHASE 4: AGENTIC LOGIC & REFACTORING (21-28)
smart_commit "feat: start pm_agent logic and playground testing" "apps/agents/pm*"
smart_commit "lab: add interactive marimo notebooks for R&D" "notebooks/" "labs/"
smart_commit "refactor: migrate core agents to pydantic-ai" "*pydantic_ai*"
smart_commit "feat: implement agentic factories and robust SLM logic" "apps/factory"
smart_commit "dev: enhance skaffold workflow for cloud-native dev" "skaffold.yaml"
smart_commit "test: add pytest suite and BDD specifications" "tests/" "pytest.ini"
smart_commit "refactor: centralize all CI/CD logic into Makefile" "Makefile"
smart_commit "naming: official rebranding to L-Architecte" "apps/architect/domain/naming.py"

# PHASE 5: STABILIZATION & FINAL (29-32)
smart_commit "fix: stabilize k8s networking and port-forwarding" "k8s/svc"
smart_commit "ci: optimize runner storage and disk pressure fixes" ".github/scripts/cleanup*"
smart_commit "feat: add healthchecks and status API" "apps/api/status"
smart_commit "fix: final production adjustments and timeouts" "." # Catch-all for remaining files

echo "Done! 323 commits squashed into 32 logical steps."