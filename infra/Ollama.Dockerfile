FROM ollama/ollama:latest

ENV OLLAMA_MODELS=/root/.ollama/models

RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    # Ultra light model
    ollama pull gemma3:270m && \
    pkill ollama

EXPOSE 11434

# Public container
LABEL org.opencontainers.image.source="https://github.com/fabienfrfr/AgenticArchitect"
LABEL org.opencontainers.image.description="TheArchitect - Ollama with light model included"