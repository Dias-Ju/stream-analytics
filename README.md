# StreamAnalytics

Plataforma de análise de streams musicais com atualização automática, desenvolvida com Kafka, Python, Flask e MySQL.

## Sobre o projeto

Este projeto nasceu como um estudo prático sobre **replicação de dados e pipelines de mensageria com Kafka** — tecnologia que utilizo no meu dia a dia como Jovem Aprendiz no PagBank.

### Evolução

**v1 — Loja de periféricos:** a primeira versão simulava pedidos de uma loja de periféricos (teclados, mouses, monitores) para entender na prática como funciona o fluxo de replicação de dados com Kafka — producer publicando eventos, consumer processando e armazenando, DLQ capturando falhas.

**v2 — Testes e aprendizado:** com a base técnica funcionando, o projeto virou um ambiente de testes para explorar conceitos mais avançados: consumer groups, particionamento por chave, retry automático, Kafka Connect e CDC com PostgreSQL.

**v3 — StreamAnalytics (versão atual):** decidi transformá-lo em algo com mais a minha cara. Mantive toda a estrutura técnica que aprendi e mudei o contexto para análise de streams musicais, com um dashboard visual inspirado na estética Y2K dos anos 2000. Os arquivos das versões anteriores estão preservados na pasta `old/` do repositório.

O projeto está em desenvolvimento contínuo e novas funcionalidades serão adicionadas.

## Como funciona

```
Producer → Kafka → Consumer → MySQL → API Flask → Dashboard
```

- O **producer** simula reproduções de músicas, incluindo comportamentos suspeitos propositais (repetição, rajadas e duração curta) para testar a detecção de bot
- O **Kafka** recebe e distribui os eventos entre as partições
- O **consumer** analisa cada stream com regras reais de detecção de bot e lógica de retry — streams suspeitos são enviados para a DLQ com o motivo detalhado
- O **MySQL** armazena os streams válidos e os filtrados separadamente
- A **API Flask** expõe os dados através de endpoints REST
- O **dashboard** exibe tudo com atualização automática a cada 10 segundos

## Tecnologias

- Apache Kafka (confluent-kafka)
- Python 3.13
- Flask + Flask-CORS
- MySQL
- HTML, CSS e JavaScript puro
- Docker
- Chart.js

## Funcionalidades

- Monitoramento de streams com atualização automática a cada 10 segundos
- Ranking de músicas e artistas mais escutados
- Ranking por período — hoje, semana ou total
- Distribuição por plataforma (Spotify, Apple Music, YouTube Music, Deezer)
- Gráfico de evolução de streams dos últimos 30 minutos
- Detecção de comportamento de bot com três regras reais:
  - **Duração suspeita** — streams com menos de 30 segundos
  - **Repetição suspeita** — mesma música reproduzida mais de 3 vezes em 5 minutos pelo mesmo usuário
  - **Volume anormal** — usuário com mais de 5 streams em 1 minuto
- Dead Letter Queue com motivo detalhado do filtro
- Painel de recados privado
- Dashboard com estética Y2K
- Script de inicialização automática (`start.bat`)

## Como rodar localmente

**Pré-requisitos:** Docker, Python 3.13, MySQL

**1. Clone o repositório:**
```bash
git clone https://github.com/Dias-Ju/stream-analytics.git
cd stream-analytics
```

**2. Crie o arquivo `.env` na raiz do projeto:**
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=kafka_monitoramento
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Crie o banco e as tabelas no MySQL:**
```sql
CREATE DATABASE IF NOT EXISTS kafka_monitoramento;
USE kafka_monitoramento;

CREATE TABLE IF NOT EXISTS streams_processados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(50),
    usuario VARCHAR(50),
    musica VARCHAR(100),
    artista VARCHAR(100),
    plataforma VARCHAR(50),
    duracao INT,
    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS streams_dlq (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stream_id VARCHAR(50),
    erro TEXT,
    tentativas INT,
    data_erro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**5. Suba o Kafka:**
```bash
docker compose up -d
```

**6. Crie o tópico no Kafka:**
```bash
docker exec -it kafka kafka-topics --create --topic meu-primeiro-topico --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

**7. Suba os serviços — cada um em um terminal separado:**
```bash
python api.py
```
```bash
python consumer.py
```
```bash
python producer.py
```

**8. Abra o `frontend/index.html` no navegador.**

> **Atalho:** no Windows você pode usar o `start.bat` com Run as administrator para subir tudo automaticamente.

## Próximos passos

- Deploy em nuvem com Terraform

---

Desenvolvido por **Júlia Dias** · Jovem Aprendiz na área de Plataforma de Dados e API