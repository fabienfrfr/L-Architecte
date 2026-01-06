FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgirepository-2.0-dev \
    libcairo2-dev \
    pkg-config \
    gir1.2-gtk-3.0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY apps/architect/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python3", "-m", "apps.architect.main"]