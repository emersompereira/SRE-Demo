# ---------------------------------------------------------------------------
# Stage 1: builder — instala dependências em um virtualenv isolado
# ---------------------------------------------------------------------------
FROM python:3.12-alpine AS builder

# Evita geração de .pyc e garante logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Copia apenas o manifesto para aproveitar cache de camadas
COPY requirements.txt .

# Instala dependências no venv separado
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — imagem final mínima, sem ferramentas de build
# ---------------------------------------------------------------------------
FROM python:3.12-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Defaults sobrescrevíveis por variável de ambiente
    APP_ENV=staging \
    PORT=8080

# Cria usuário e grupo não-root
RUN addgroup -g 1001 -S appgroup && \
    adduser  -u 1001 -S appuser -G appgroup

WORKDIR /app

# Copia apenas o venv do estágio anterior (sem pip, compiladores, etc.)
COPY --from=builder /opt/venv /opt/venv

# Copia o código-fonte
COPY app/ .

# Ajusta dono dos arquivos
RUN chown -R appuser:appgroup /app

# Usa o usuário não-root
USER appuser

# Expõe a porta configurável
EXPOSE ${PORT}

# Ativa o venv e sobe o servidor
CMD ["/opt/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
