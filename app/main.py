import os
import time
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ---------------------------------------------------------------------------
# Configurações via variáveis de ambiente
# ---------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "staging")
PORT    = int(os.getenv("PORT", "8080"))

# ---------------------------------------------------------------------------
# Logging estruturado para stdout (formato esperado pelo Logstash/Filebeat)
# Formato: 2026-01-01T00:00:00Z INFO /endpoint latency=12ms
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Métricas Prometheus
# ---------------------------------------------------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requisições HTTP",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Latência das requisições HTTP em segundos",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

ERROR_RATE = Gauge(
    "http_error_rate",
    "Taxa de erros (requisições com status ≥ 500)",
)

IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requisições em andamento",
)

# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SRE Demo App",
    description="Aplicação de exemplo para teste SRE Pleno",
    version="1.0.0",
)

# Middleware: registra métricas e loga cada requisição
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    endpoint = request.url.path
    method   = request.method

    IN_PROGRESS.inc()
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.error(f"{endpoint} latency={latency_ms:.2f}ms error={exc}")
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=500).inc()
        ERROR_RATE.inc()
        raise
    finally:
        IN_PROGRESS.dec()

    latency_s  = time.perf_counter() - start
    latency_ms = latency_s * 1000
    status     = response.status_code

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency_s)

    if status >= 500:
        ERROR_RATE.inc()
        logger.error(f"{endpoint} latency={latency_ms:.2f}ms status={status}")
    elif status >= 400:
        logger.warning(f"{endpoint} latency={latency_ms:.2f}ms status={status}")
    else:
        logger.info(f"{endpoint} latency={latency_ms:.2f}ms status={status}")

    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Endpoint principal — retorna ambiente e timestamp."""
    return {
        "app": "sre-demo",
        "env": APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    """Liveness probe — informa se o processo está vivo."""
    return JSONResponse(status_code=200, content={"status": "healthy"})


@app.get("/ready")
async def ready():
    """Readiness probe — informa se o app está pronto para receber tráfego."""
    return JSONResponse(status_code=200, content={"status": "ready"})


@app.get("/metrics")
async def metrics():
    """Endpoint scrapeado pelo Prometheus."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
