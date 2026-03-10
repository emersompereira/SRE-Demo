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

# Copia o código-fonte ajustando o dono em uma única instrução (Otimização de Layers)
COPY --chown=appuser:appgroup app/ .

# Usa o usuário não-root (Segurança)
USER appuser

# Expõe a porta configurável
EXPOSE ${PORT}

# Executa usando o formato JSON (exec form) recomendado, mas com shell para interpolar a variável $PORT
# O "exec" garante que o Uvicorn receba os sinais de SO (como SIGTERM) corretamente em vez do shell
CMD ["sh", "-c", "exec /opt/venv/bin/uvicorn main:app --host 0.0.0.0 --port $PORT"]
