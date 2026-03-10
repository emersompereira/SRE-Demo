# SRE Pleno Test - Emersom Pereira

## 🚀 Quick Start

### Pré-requisitos
- Docker instalado
- (para K8s) Kind ou Minikube
- Git (clonar repositório)
- kubectl (interação com cluster k8s)
- helm (gerenciar pacotes k8s)

### Rodando localmente com Docker

```bash
# Build da imagem (adicione --no-cache se houver problemas de build/cache)
docker build -t sre-demo:latest .

# Executar o container na porta padrão (8080)
docker run -d -p 8080:8080 \
  -e APP_ENV=staging \
  -e PORT=8080 \
  --name sre-demo-app \
  sre-demo:latest

# Executar o container modificando o ambiente e a porta (Exemplo de Flexibilidade)
docker run -d -p 9000:9000 \
  -e PORT=9000 \
  -e APP_ENV=production \
  --name sre-demo-app-prod \
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
└── .github/workflows/   # Pipeline CI/CD com GitHub Actions (Tarefa 4)
    └── pipeline.yaml
```

---

## 📋 Componentes

- **App:** API em FastAPI c/ Python 3.12 usando `uvicorn`. Possui documentação automática e probes `/health`, `/ready` e `/metrics`.
- **K8s:** Deployment configurado via ConfigMap nativo e referências em Variável de ambiente, service exposto via `NodePort` (30080) e escalabilidade dinâmica (HPA v2 auto-scaling) com base em limite de RAM e CPU.
- **Monitoring:** Scraping automático no Prometheus via Native Kubernetes deployment annotations (`prometheus.io/scrape`). O Dashboard centraliza e mede requisições (por segundo/totais), latência no 95º percentil (P95) e taxa de erro 5xx.
- **CI/CD:** GitHub Actions que abrange validações de Docker (Lint) com hadolint, Build, Push para o repo de pacotes GitHub Registry (GHCR) e simula a consistência deploy de Kubernetes em Action usando cluster efêmero.
- **ELK:** [Omitido do escopo desta implementação]

### App e Variáveis de Ambiente
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
| **Logs em stdout** | Padrão 12-factor app; facilita captação de logs por rotadores de Kubernetes |
| **CMD c/ exec form e shell** | Garante interpolação de variáveis de ambiente (`$PORT`) enquanto mantém o repasse correto de sinais (`SIGTERM`) para graceful shutdown |
| **Testes Efêmeros CI/CD** | Uso do `helm/kind-action` para simular consistência k8s nativamente na pipeline no estilo "Clean Room", diminuindo risco de deployments com falha de sintaxe na master |
