from confluent_kafka import Consumer
import json

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'grupo-final',
    'auto.offset.reset': 'earliest'
})

TOPICO_DESTINO = 'pedidos-replicados'

consumer.subscribe([TOPICO_DESTINO])

print("Consumindo dados finais (simulando DataX)...")
print("-" * 60)

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print(f"Erro: {msg.error()}")
        continue

    evento = json.loads(msg.value().decode('utf-8'))

    print(f"Pedido final:")
    print(f"ID       : {evento['pedido_id']}")
    print(f"Usuário  : {evento['usuario']}")
    print(f"Produto  : {evento['produto']}")
    print(f"Preço    : R${evento['preco']}")
    print(f"Status   : {evento['status']}")
    print("-" * 60)