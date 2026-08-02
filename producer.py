from confluent_kafka import Producer
import time
import random
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

usuarios = [
    'Julia',
    'Ana',
    'Leo',
    'Rafa',
    'Mike',
    'Clara',
    'Nina'
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
    'Spotify',
    'YouTube Music',
    'Apple Music',
    'Deezer'
]

print("Simulando streams musicais em tempo real...")

while True:

    usuario = random.choice(usuarios)

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

    print(
        f"Stream → "
        f"{stream_id} | "
        f"{usuario} | "
        f"{musica} | "
        f"{artista}"
    )

    producer.flush()

    time.sleep(2)