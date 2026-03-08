**TAREFA 1:** 



CRiei a aplicação com ajuda da IA;

Escolhi python e FastAIP porque.........





COMANDOS UTILIZADOS



**Build da imagem:**

*docker build -t sre-demo:latest .*

Explicar comando.......

**Criar cluster**
kind create cluster

**Carregar imagem no Kind:**

*kind load docker-image sre-demo:latest*

explicar comando.....



**Aplicar manifestos k8s:**

*kubectl apply -f k8s/configmap.yaml*

*kubectl apply -f k8s/deployment.yaml*

*kubectl apply -f k8s/service.yaml*

*kubectl apply -f k8s/hpa.yaml*



**Mapeamento de porta entre host e o cluster:**

*kubectl port-forward svc/sre-demo 8080:8080* ou *kubectl port-forward --address 0.0.0.0 svc/sre-demo 8080:8080* **para acessar com IP público.**

**Observação sobre ServiceMonitor (Prometheus)**

- O `ServiceMonitor` que o Prometheus usa para descobrir a app foi aplicado no namespace `default`.
- Arquivo usado: `k8s/servicemonitor-sre-demo-default.yaml`.

**instalação da stack do Prometheus com helm**

*helm repo add prometheus-community https://prometheus-community.github.io/helm-charts*

*helm repo update*

kubectl create namespace monitoring


kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# abrir http://localhost:9090/targets


kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# abrir http://localhost:3000  (usuário/senha padrão configurados pelo chart)


$pw = kubectl get secret --namespace monitoring -l app.kubernetes.io/component=admin-secret -o jsonpath="{.items[0].data['admin-password']}"
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($pw))
# Senha grafana





