# --- Etapa 1: Constructor ---
FROM python:3.12-slim AS builder

# Instalamos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copiamos archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalamos dependencias en un entorno aislado (sin paquetes de desarrollo)
RUN uv sync --frozen --no-dev

# --- Etapa 2: Ejecución ---
FROM python:3.12-slim

WORKDIR /app

# Copiamos solo el entorno virtual y el código desde el constructor
COPY --from=builder /app/.venv /app/.venv
COPY ./app /app/app

# Variables de entorno
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Exponemos el puerto
EXPOSE 8000

# Ejecutamos con Granian (notarás que no usamos --reload en producción)
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "app.main:app"]