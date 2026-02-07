FROM python:3.13-slim-bookworm

# System dependencies for gobject-introspection and builds
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    #ninja-build \
    python3-dev \
    #libgirepository1.0-dev \
    #gobject-introspection \
    #libglib2.0-dev \
    #libcairo2-dev \
    #gir1.2-gtk-3.0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PKG_CONFIG_PATH="/usr/lib/$(uname -m)-linux-gnu/pkgconfig:/usr/share/pkgconfig"
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Pre-install dependencies to leverage Docker cache
COPY pyproject.toml uv.lock ./
COPY apps/architect/pyproject.toml ./apps/architect/
RUN uv sync --frozen --no-dev --no-install-project

# Copy & Install the entire project
COPY . .
RUN uv sync --frozen --no-dev

# Metadata
EXPOSE 8080 5678

# Public container
LABEL org.opencontainers.image.source="https://github.com/fabienfrfr/AgenticArchitect"
LABEL org.opencontainers.image.description="TheArchitect - Agentic Architect Core"

# ENV PYTHON_JIT=1 (if need optimization)
CMD ["python", "apps/architect/main.py"]