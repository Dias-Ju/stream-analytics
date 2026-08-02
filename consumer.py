from confluent_kafka import Consumer, Producer
import json
import random
import time
import mysql.connector
from dotenv import load_dotenv
import os

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

print("Processando streams musicais em tempo real...")
print("-" * 60)

def processar_stream(evento):
    if random.random() < 0.6:
        raise Exception("Stream identificado como suspeito pela plataforma!")
    return True

def enviar_para_dlq(mensagem, evento, erro):

    dlq_evento = {
        'stream_original': evento,
        'erro': str(erro),
        'tentativas': MAX_TENTATIVAS
    }

    dlq_producer.produce(
        'dlq-streams',
        key=mensagem.key(),
        value=json.dumps(dlq_evento).encode('utf-8')
    )

    dlq_producer.flush()

    # with open('dlq_streams.jsonl', 'a', encoding='utf-8') as f:
    #     import os

    #     print("SALVANDO EM:", os.getcwd())

    #     f.write(json.dumps(dlq_evento, ensure_ascii=False) + '\n')

    sql = """
    INSERT INTO streams_dlq
    (stream_id, erro, tentativas)
    VALUES (%s, %s, %s)
    """

    valores = (
        evento['stream_id'],
        str(erro),
        MAX_TENTATIVAS
    )

    cursor.execute(sql, valores)

    db.commit()

    print(f"DLQ | {evento['stream_id']} | enviado após {MAX_TENTATIVAS} tentativas")

while True:

    mensagem = consumer.poll(1.0)

    if mensagem is None:
        continue

    if mensagem.error():
        print(f"Erro Kafka: {mensagem.error()}")
        continue

    evento = json.loads(mensagem.value().decode('utf-8'))

    sucesso = False
    ultimo_erro = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:
            processar_stream(evento)

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

        # with open('streams_processados.jsonl', 'a', encoding='utf-8') as f:
        #     f.write(json.dumps(evento, ensure_ascii=False) + '\n')

        sql = """
        INSERT INTO streams_processados
        (stream_id, usuario, musica, artista, plataforma, duracao)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        valores = (
            evento['stream_id'],
            evento['usuario'],
            evento['musica'],
            evento['artista'],
            evento['plataforma'],
            evento['duracao']
        )

        cursor.execute(sql, valores)

        db.commit()

        consumer.commit(mensagem)

        print(f"✅ Processado | {evento['stream_id']} | {evento['musica']} | {evento['artista']} | REPLICADO | SALVO")

    else:

        enviar_para_dlq(mensagem, evento, ultimo_erro)

        consumer.commit(mensagem)

    print("-" * 60)