# eventos-soap

Aplicação SOAP de gerenciamento de eventos com servidor Python (Spyne) e cliente Java (JAX-WS).

## Executando com Docker

```bash
# Subir o servidor
docker compose up -d --build server

# Executar o cliente interativo
docker compose run --rm client

# Ver as últimas 50 linhas em tempo real
docker compose logs -f --tail=50 server

# Encerrar
docker compose down
```
