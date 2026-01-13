FROM ollama/ollama:latest

RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama pull gemma3:270m && \
    pkill ollama

EXPOSE 11434