# Instalar ELK localmente (exemplo com Helm)

Este guia instala uma versão de desenvolvimento/teste do Elasticsearch, Kibana e Filebeat usando os charts oficiais da Elastic.

ATENÇÃO: charts de produção requerem mais memória, storage e configuração de segurança. Os valores aqui são para uso local (Kind/minikube).

Pré-requisitos
- `helm` instalado
- cluster Kubernetes (Kind/Minikube) com recursos suficientes

1) Adicionar o repo da Elastic

```bash
helm repo add elastic https://helm.elastic.co
helm repo update
```

2) Instalar Elasticsearch (single-node para testes)

```bash
kubectl create namespace elk || true
helm install elasticsearch elastic/elasticsearch -n elk -f elk/elasticsearch-values.yaml
```

3) Instalar Kibana

```bash
helm install kibana elastic/kibana -n elk -f elk/kibana-values.yaml
```

4) Instalar Filebeat (DaemonSet)

```bash
helm install filebeat elastic/filebeat -n elk -f elk/filebeat-values.yaml
```

5) Acessar Kibana (exemplo usando port-forward)

```bash
# porta 5601 local -> kibana service (ajuste se necessário)
kubectl -n elk port-forward svc/kibana-kibana 5601:5601
# depois abra http://localhost:5601
```

Observações e troubleshooting
- Se o chart da Elastic exigir segurança/credentials, consulte a documentação oficial: https://www.elastic.co/guide/en/elastic-stack/current/index.html
- Para Kind é comum reduzir réplicas e desabilitar persistência: já feito nos valores fornecidos.
- Se preferir evitar Helm, você pode aplicar manifestos manualmente (há `elk/filebeat.yaml` e `elk/logstash.conf` no repositório). Esses arquivos podem ser adaptados para usar Logstash como collector em vez de enviar direto para Elasticsearch.

Quer que eu execute os comandos exatos para você gerar os releases do Helm (apenas os arquivos/commits serão criados aqui — não tenho acesso direto ao seu cluster)?
