#!/bin/bash

# =================================================================
# AgenticArchitect - Docker Launch Script
# Author: Fabien Furfaro
# =================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}--- Launching AgenticArchitect with Docker ---${NC}"

# 1. Check if docker-compose.yml exists
if [ ! -f "infra/docker-compose.yml" ]; then
    echo -e "${RED}[ERROR] infra/docker-compose.yml not found!${NC}"
    exit 1
fi

# 2. Starting containers
echo -e "${GREEN}[1/2] Starting containers...${NC}"
docker-compose -f infra/docker-compose.yml up -d

# 3. Ensuring gemma270m is available
# We use 'ollama pull' to ensure the model is downloaded as requested
echo -e "${GREEN}[2/2] Checking LLM model (gemma270m)...${NC}"
docker exec -it ollama-container-name ollama pull gemma:2b

echo -e "${BLUE}--- Application is ready at http://localhost:8080 ---${NC}"
echo "Displaying logs (Press Ctrl+C to stop)..."
docker-compose -f infra/docker-compose.yml logs -f app