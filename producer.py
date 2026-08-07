from confluent_kafka import Producer
import time
import random
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

usuarios = [
    'Julia', 'Ana', 'Leo', 'Rafa', 'Mike', 'Clara', 'Nina'
]

musicas = [
    ('Please', 'BTS'),
    ('Drag Path', 'Twenty One Pilots'),
    ('Sienna', 'The Marías'),
    ('As It Was', 'Harry Styles'),
    ('Futile Devices', 'Sufjan Stevens'),
    ('Creep', 'Radiohead'),
    ('Ew', 'Joji')
]

plataformas = [
    'Spotify', 'YouTube Music', 'Apple Music', 'Deezer'
]

print("Simulando streams musicais em tempo real...")

historico_bot = {}

while True:

    chance = random.random()

    # 10% de chance de stream com duração muito curta
    if chance < 0.10:
        usuario = random.choice(usuarios)
        musica, artista = random.choice(musicas)
        duracao = random.randint(5, 29)
        tipo = 'curto'

    # 10% de chance de repetição da mesma música
    elif chance < 0.20:
        usuario = random.choice(usuarios)
        musica, artista = random.choice(musicas)
        duracao = random.randint(120, 320)
        for _ in range(random.randint(3, 6)):
            stream_id = f"stream_{random.randint(1000, 9999)}"
            evento = {
                'stream_id': stream_id,
                'usuario': usuario,
                'musica': musica,
                'artista': artista,
                'plataforma': random.choice(plataformas),
                'duracao': duracao
            }
            producer.produce(
                'meu-primeiro-topico',
                key=stream_id.encode('utf-8'),
                value=json.dumps(evento).encode('utf-8')
            )
            print(f"Stream (repetição) → {stream_id} | {usuario} | {musica}")
            producer.flush()
            time.sleep(0.2)
        time.sleep(2)
        continue

    # 5% de chance de rajada de streams (volume anormal)
    elif chance < 0.25:
        usuario = random.choice(usuarios)
        for _ in range(random.randint(6, 10)):
            musica, artista = random.choice(musicas)
            stream_id = f"stream_{random.randint(1000, 9999)}"
            evento = {
                'stream_id': stream_id,
                'usuario': usuario,
                'musica': musica,
                'artista': artista,
                'plataforma': random.choice(plataformas),
                'duracao': random.randint(120, 320)
            }
            producer.produce(
                'meu-primeiro-topico',
                key=stream_id.encode('utf-8'),
                value=json.dumps(evento).encode('utf-8')
            )
            print(f"Stream (rajada) → {stream_id} | {usuario} | {musica}")
            producer.flush()
            time.sleep(0.1)
        time.sleep(2)
        continue

    # 75% stream normal
    else:
        usuario = random.choice(usuarios)
        musica, artista = random.choice(musicas)
        duracao = random.randint(120, 320)
        tipo = 'normal'

    stream_id = f"stream_{random.randint(1000, 9999)}"

    evento = {
        'stream_id': stream_id,
        'usuario': usuario,
        'musica': musica,
        'artista': artista,
        'plataforma': random.choice(plataformas),
        'duracao': duracao
    }

    producer.produce(
        'meu-primeiro-topico',
        key=stream_id.encode('utf-8'),
        value=json.dumps(evento).encode('utf-8')
    )

    print(f"Stream → {stream_id} | {usuario} | {musica} | {duracao}s")
    producer.flush()
    time.sleep(2)