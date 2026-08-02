# StreamAnalytics
 
Plataforma de análise de streams musicais em tempo real, desenvolvida com Kafka, Python, Flask e MySQL.
 
## Sobre o projeto
 
Este projeto nasceu como um estudo prático sobre **replicação de dados e pipelines de mensageria com Kafka** — tecnologia que utilizo no meu dia a dia como Jovem Aprendiz no PagBank. Com o tempo, decidi transformá-lo em algo mais pessoal: um analisador de streams musicais em tempo real, com um dashboard visual inspirado na estética Y2K dos anos 2000.
 
O projeto está em desenvolvimento contínuo e novas funcionalidades serão adicionadas ao longo da minha jornada profissional.
 
## Como funciona
 
```
Producer → Kafka → Consumer → MySQL → API Flask → Dashboard
```
 
- O **producer** simula reproduções de músicas em tempo real
- O **Kafka** recebe e distribui os eventos entre as partições
- O **consumer** processa cada stream com lógica de retry e DLQ — streams suspeitos são filtrados e enviados para uma fila separada
- O **MySQL** armazena os streams válidos e os filtrados
- A **API Flask** expõe os dados através de endpoints REST
- O **dashboard** exibe tudo em tempo real com rankings, métricas e feed ao vivo
## Tecnologias
 
- Apache Kafka (confluent-kafka)
- Python 3.13
- Flask + Flask-CORS
- MySQL
- HTML, CSS e JavaScript puro
- Docker
## Funcionalidades
 
- Monitoramento de streams em tempo real
- Ranking de músicas e artistas mais escutados
- Distribuição por plataforma (Spotify, Apple Music, YouTube Music, Deezer)
- Detecção de streams suspeitos com retry automático e Dead Letter Queue
- Painel de recados privado
- Dashboard com estética Y2K
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
 
**4. Suba o Kafka:**
```bash
docker compose up -d
```
 
**5. Crie o banco e as tabelas no MySQL:**
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
 
**6. Crie o tópico no Kafka:**
```bash
docker exec -it kafka kafka-topics --create --topic meu-primeiro-topico --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```
 
**7. Suba os serviços em terminais separados:**
```bash
python api.py
python consumer.py
python producer.py
```
 
**8. Abra o `frontend/index.html` no navegador.**
 
## Próximos passos
 
- Gráficos de evolução de streams ao longo do tempo
- Ranking diário e semanal
- Detecção de comportamento de bot
- Deploy em nuvem
---
 
Desenvolvido por **Júlia Dias** · Jovem Aprendiz na área de Plataforma de Dados e API