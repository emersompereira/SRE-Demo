#  Guia de Referência e Comandos Utilizados

Este documento serve como um roteiro didático de como o projeto foi estruturado, quais decisões foram tomadas e os comandos necessários para reproduzir o ambiente localmente.

---

## 1. Justificativa de Tecnologias

**Por que Python e FastAPI?**
Foi escolhido o **FastAPI** devido à sua alta performance baseada em concorrência assíncrona (Starlette), rápida curva de aprendizado e por possuir excelente instrumentação para observabilidade. Para microsserviços modernos sob a ótica de SRE, ele fornece um consumo de recursos extremamente otimizado (baixo pé de memória comparado ao Django/Flask), auto-documentação (Swagger nativo) e facilita a exposição da rota /metrics no formato que o Prometheus exige nativamente via bibliotecas oficiais.

---

## 2. Containerização (Docker)

**Construção da imagem Docker:**
``bash
docker build -t sre-demo:latest .
``
> **O que esse comando faz?** Lê o Dockerfile no diretório atual e cria uma imagem do app baseada na arquitetura Multi-stage build para que a imagem final seja mínima (apenas Alpine + binários do Python sem dependências de compilações) em nome da segurança. A tag latest define a versão atual.

---

## 3. Criação do Cluster Local (Kind)

O Kind (Kubernetes in Docker) é usado para emular ambientes em k8s limpos para testes.

**Levantar o cluster:**
``bash
kind create cluster --name sre-cluster
``

**Sideload da imagem para dentro do cluster:**
``bash
kind load docker-image sre-demo:latest --name sre-cluster
``
> **Explicação importante:** O cluster do kind está isolado no seu próprio container Docker. Se não enviarmos (sideload) a nossa imagem local para ele dessa forma, ele tentará baixar o "sre-demo:latest" da internet (Docker Hub) e falhará (ImagePullBackOff).

---

## 4. Deploy da Aplicação no Kubernetes

**Aplicar os manifestos da aplicação:**
``bash
kubectl apply -f k8s/deployment.yaml
``
> Passar uma pasta (invés de um único arquivo) faz com que o Kubernetes avalie e aplique todos os manifestos de dentro do repositório de uma vez (deployment.yaml, service.yaml, hpa.yaml).

**OBS.:Nesse projeto ainda é necessário a aplicação dos manifestos um por vez, pois ainda não está 100% otimizado** 
kubectl apply -f k8s/deployment.yaml - Configuração da aplicação, alocação de recursos, quantidade de répiclas e etc.
kubectl apply -f k8s/hpa.yaml - Configuração do AutoScaler horizontal
apply -f k8s/service.yaml - Exposição da aplicação
apply -f k8s/metrics-server.yaml - Instalação do metrics-server para agregar as métricas

**Mapeamento de porta da aplicação para Host:**
``bash
kubectl port-forward svc/sre-demo 8080:8080
# Ou exportando para um IP Público (Máquinas AWS/Cloud):
kubectl port-forward --address 0.0.0.0 svc/sre-demo 8080:8080 > /dev/null 2>&1 &
``

---

## 5. Instalando Observabilidade (Stack Prometheus + Grafana)

**Preparar os repositórios oficiais via Helm e instalar o Kube-Prometheus-Stack:**
``bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Criação do ambiente isolado (Namespace)
kubectl create namespace monitoring

# Instalação com deploy massivo de Operators
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
``

**Garantir o descobrimento de métricas da nossa App:**
``bash
kubectl apply -f k8s/servicemonitor-sre-demo-default.yaml
``
> O ServiceMonitor notifica dinamicamente a stack Prometheus dentro do monitoring para olhar as métricas do nosso namespace configurado.

---

## 6. Acesso aos Dashboards (Monitoring)

**Acessar a interface do Prometheus Localmente:**
``bash
local: kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
IP público: kubectl port-forward --address 0.0.0.0 -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 > /dev/null 2>&1 &
``
> Abra http://localhost:9090/targets para conferir a saúde do scrape da sua aplicação.
ou
http://IP-publico:9090/targets

**Acessar a interface do Grafana:**
``bash
local: kubectl port-forward  -n monitoring svc/prometheus-grafana 3000:80
IP público: kubectl port-forward --address 0.0.0.0 -n monitoring svc/prometheus-grafana 3000:80 > /dev/null 2>&1 &
``
> Acesse http://localhost:3000. O usuário de login padrão será admin.
ou
http://IP-publico:3000

**Coletar senha raiz gerada pelo Helm para o Grafana:**
``bash
kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
``
> O terminal exibirá uma senha aleatória que você usa em conjunto com admin para visualizar o Dashboard providenciado na pasta /monitoring.
