#!/bin/bash
docker-compose -f ../infra/docker-compose.yml exec chromadb python -c "
import chromadb
client = chromadb.HttpClient(host='chromadb', port=8000)
client.create_collection(name='cdc_docs')
print('✅ ChromaDB initialized.')
"
