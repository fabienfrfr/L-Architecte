FROM ollama/ollama

RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama pull gemma3:270m