# SRE Pleno Test

## 🚀 Quick Start

### Pré-requisitos
- Docker instalado
- (para K8s) Kind ou Minikube

### Rodando localmente com Docker

```bash
# Build da imagem
docker build -t sre-demo:latest .

# Executar o container
docker run -p 8080:8080 \
  -e APP_ENV=staging \
  -e PORT=8080 \
  sre-demo:latest
```

### Testando os endpoints

```bash
# Página inicial
curl http://localhost:8080/

# Liveness probe
curl http://localhost:8080/health

# Readiness probe
curl http://localhost:8080/ready

# Métricas Prometheus
curl http://localhost:8080/metrics
```

---

## 🏗 Arquitetura

```
sre-pleno-test/
├── Dockerfile           # Multi-stage build (builder + runtime)
├── requirements.txt     # Dependências Python
├── .dockerignore        # Arquivos excluídos do contexto Docker
├── app/
│   └── main.py          # Aplicação FastAPI
├── k8s/                 # Manifestos Kubernetes (Tarefa 2)
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── monitoring/          # Observabilidade (Tarefa 3)
│   └── grafana-dashboard.json
├── ci/                  # Pipeline CI/CD (Tarefa 4)
│   └── pipeline.yaml
└── elk/                 # Stack ELK (Tarefa 5)
    ├── filebeat.yaml
    ├── logstash.conf
    └── kibana-dashboard.json
```

---

## 📋 Componentes

### App (FastAPI + Python 3.12)
- **`/`** — Retorna ambiente (`APP_ENV`) e timestamp UTC.
- **`/health`** — Liveness probe, retorna `200 OK`.
- **`/ready`** — Readiness probe, retorna `200 OK`.
- **`/metrics`** — Endpoint scrapeado pelo Prometheus.

### Variáveis de Ambiente
| Variável  | Padrão    | Descrição                        |
|-----------|-----------|----------------------------------|
| `APP_ENV` | `staging` | Ambiente da aplicação            |
| `PORT`    | `8080`    | Porta em que o servidor escuta   |

### Métricas expostas (`/metrics`)
| Métrica                          | Tipo      | Descrição                            |
|----------------------------------|-----------|--------------------------------------|
| `http_requests_total`            | Counter   | Total de requisições por rota/status |
| `http_request_duration_seconds`  | Histogram | Latência das requisições             |
| `http_error_rate`                | Gauge     | Requisições com status ≥ 500         |
| `http_requests_in_progress`      | Gauge     | Requisições sendo processadas        |

### Formato de Log (stdout)
```
2026-03-03T17:00:00Z INFO /health latency=1.23ms status=200
2026-03-03T17:00:01Z ERROR /api latency=300.00ms error=<msg>
```
Timestamp ISO 8601 + nível + endpoint + latência — compatível com o grok do Logstash.

---

## 🔧 Decisões Técnicas

| Decisão | Justificativa |
|---|---|
| **Python 3.12-alpine** | Imagem base oficial e mínima, reduz superfície de ataque |
| **Multi-stage build** | Stage `builder` isola dependências; `runtime` não contém pip/compiladores |
| **Usuário não-root (UID 1001)** | Segurança: container não roda como root |
| **FastAPI + uvicorn** | Framework assíncrono, simples, com suporte nativo a JSON e middleware |
| **prometheus-client** | Biblioteca oficial; integração direta com Prometheus sem agent externo |
| **Logs em stdout** | Padrão 12-factor app; Filebeat captura automaticamente via K8s |
