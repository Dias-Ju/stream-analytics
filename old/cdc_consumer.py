from confluent_kafka import Consumer
import json
import base64
from datetime import datetime

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'grupo-cdc-2',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['ecommerce.public.pedidos'])
print('Monitorando mudancas no banco...')
print('-' * 60)

def decodificar_decimal(valor_base64):
    try:
        bytes_valor = base64.b64decode(valor_base64)
        numero = int.from_bytes(bytes_valor, byteorder='big')
        return numero / 100
    except:
        return valor_base64

def decodificar_timestamp(micros):
    try:
        return datetime.fromtimestamp(micros / 1_000_000).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return micros

operacoes = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f'Erro: {msg.error()}')
        continue

    if msg.value() is None:
        continue

    evento = json.loads(msg.value().decode('utf-8'))
    payload = evento.get('payload', {})
    op = payload.get('op', '')

    if op == 'd':
        dados = payload.get('before', {})
    else:
        dados = payload.get('after', {})

    if not dados:
        continue

    print(f"Operação : {operacoes.get(op, op)}")
    print(f"ID       : {dados.get('id')}")
    print(f"Usuario  : {dados.get('usuario')}")
    print(f"Produto  : {dados.get('produto')}")
    print(f"Preço    : R${decodificar_decimal(dados.get('preco', 0))}")
    print(f"Status   : {dados.get('status')}")
    print(f"Criado em: {decodificar_timestamp(dados.get('criado_em'))}")
    print('-' * 60)