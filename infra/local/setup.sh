#!/bin/bash

# Start services
docker-compose up -d chromadb ollama

# Pull the Nemotron-3 model (quantized)
docker exec -it ollama ollama pull nemotron-3-nano:30b

# Start architect service
docker-compose up -d architect 

echo "✅ Local environment ready! Access the app at http://localhost:3000"
