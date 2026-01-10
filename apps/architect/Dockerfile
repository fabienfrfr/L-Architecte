FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    ninja-build \
    python3-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    libglib2.0-dev \
    libcairo2-dev \
    gir1.2-gtk-3.0 \
    && rm -rf /var/lib/apt/lists/*

# Fix for girepository-2.0.pc not being found
RUN ln -s /usr/lib/$(uname -m)-linux-gnu/pkgconfig/gobject-introspection-1.0.pc \
    /usr/lib/$(uname -m)-linux-gnu/pkgconfig/girepository-2.0.pc

WORKDIR /app

COPY apps/architect/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python3", "-m", "apps.architect.main"]