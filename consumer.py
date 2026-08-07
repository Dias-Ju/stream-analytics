from confluent_kafka import Consumer, Producer
import json
import time
import mysql.connector
from dotenv import load_dotenv
import os
from collections import defaultdict
from datetime import datetime, timedelta

load_dotenv()

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'grupo-robusto',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False
})

dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})
replica_producer = Producer({'bootstrap.servers': 'localhost:9092'})

db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = db.cursor()

TOPICO_DESTINO = 'streams-replicados'
consumer.subscribe(['meu-primeiro-topico'])

MAX_TENTATIVAS = 3
ESPERA_ENTRE_TENTATIVAS = 2

# histórico pra detecção de bot
historico_usuario = defaultdict(list)
historico_repeticao = defaultdict(list)

print("Processando streams musicais em tempo real...")
print("-" * 60)

def detectar_bot(evento):
    usuario = evento['usuario']
    musica = evento['musica']
    duracao = evento['duracao']
    agora = datetime.now()

    # regra 1: duração muito curta
    if duracao < 30:
        return f"Duração suspeita: {duracao}s (mínimo 30s)"

    # regra 2: mesmo usuário + mesma música repetida
    chave_repeticao = f"{usuario}:{musica}"
    historico_repeticao[chave_repeticao] = [
        t for t in historico_repeticao[chave_repeticao]
        if agora - t < timedelta(minutes=5)
    ]
    historico_repeticao[chave_repeticao].append(agora)
    if len(historico_repeticao[chave_repeticao]) > 3:
        return f"Repetição suspeita: {musica} reproduzida {len(historico_repeticao[chave_repeticao])}x em 5 minutos"

    # regra 3: volume anormal (muitos streams do mesmo usuário)
    historico_usuario[usuario] = [
        t for t in historico_usuario[usuario]
        if agora - t < timedelta(minutes=1)
    ]
    historico_usuario[usuario].append(agora)
    if len(historico_usuario[usuario]) > 5:
        return f"Volume anormal: {usuario} enviou {len(historico_usuario[usuario])} streams em 1 minuto"

    return None

def enviar_para_dlq(mensagem, evento, motivo):
    dlq_evento = {
        'stream_original': evento,
        'erro': motivo,
        'tentativas': MAX_TENTATIVAS
    }

    dlq_producer.produce(
        'dlq-streams',
        key=mensagem.key(),
        value=json.dumps(dlq_evento).encode('utf-8')
    )
    dlq_producer.flush()

    sql = """
    INSERT INTO streams_dlq (stream_id, erro, tentativas)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (evento['stream_id'], motivo, MAX_TENTATIVAS))
    db.commit()
    print(f"DLQ | {evento['stream_id']} | {motivo}")

while True:
    mensagem = consumer.poll(1.0)

    if mensagem is None:
        continue
    if mensagem.error():
        print(f"Erro Kafka: {mensagem.error()}")
        continue

    evento = json.loads(mensagem.value().decode('utf-8'))

    # detecta bot
    motivo_bot = detectar_bot(evento)

    if motivo_bot:
        enviar_para_dlq(mensagem, evento, motivo_bot)
        consumer.commit(mensagem)
        print("-" * 60)
        continue

    # processa normalmente com retry
    sucesso = False
    ultimo_erro = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            sucesso = True
            break
        except Exception as e:
            ultimo_erro = e
            print(f"Tentativa {tentativa}/{MAX_TENTATIVAS} | {evento['stream_id']} | {e}")
            if tentativa < MAX_TENTATIVAS:
                time.sleep(ESPERA_ENTRE_TENTATIVAS)

    if sucesso:
        replica_producer.produce(
            TOPICO_DESTINO,
            key=mensagem.key(),
            value=mensagem.value()
        )
        replica_producer.flush()

        sql = """
        INSERT INTO streams_processados
        (stream_id, usuario, musica, artista, plataforma, duracao)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            evento['stream_id'],
            evento['usuario'],
            evento['musica'],
            evento['artista'],
            evento['plataforma'],
            evento['duracao']
        ))
        db.commit()
        consumer.commit(mensagem)
        print(f"Processado | {evento['stream_id']} | {evento['musica']} | {evento['artista']}")
    else:
        enviar_para_dlq(mensagem, evento, str(ultimo_erro))
        consumer.commit(mensagem)

    print("-" * 60)