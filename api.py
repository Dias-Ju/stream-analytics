from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

def conectar():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

@app.route('/resumo')
def resumo():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM streams_processados")
    streams_validos = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) AS total FROM streams_dlq")
    streams_suspeitos = cursor.fetchone()['total']
    total_geral = streams_validos + streams_suspeitos
    taxa_falha = 0
    if total_geral > 0:
        taxa_falha = round((streams_suspeitos / total_geral) * 100, 2)
    cursor.close()
    db.close()
    return jsonify({
        'streams_validos': streams_validos,
        'streams_suspeitos': streams_suspeitos,
        'total_geral': total_geral,
        'taxa_falha': taxa_falha
    })

@app.route('/streams')
def streams():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT stream_id, usuario, musica, artista, plataforma, duracao, data_processamento
        FROM streams_processados
        ORDER BY id DESC
        LIMIT 20
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

@app.route('/erros')
def erros():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT stream_id, erro, tentativas, data_erro
        FROM streams_dlq
        ORDER BY id DESC
        LIMIT 20
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

@app.route('/ranking/musicas')
def ranking_musicas():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT musica, artista, COUNT(*) AS total
        FROM streams_processados
        GROUP BY musica, artista
        ORDER BY total DESC
        LIMIT 10
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

@app.route('/ranking/artistas')
def ranking_artistas():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT artista, COUNT(*) AS total
        FROM streams_processados
        GROUP BY artista
        ORDER BY total DESC
        LIMIT 10
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

@app.route('/ranking/plataformas')
def ranking_plataformas():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT plataforma, COUNT(*) AS total
        FROM streams_processados
        GROUP BY plataforma
        ORDER BY total DESC
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

@app.route('/evolucao')
def evolucao():
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            DATE_FORMAT(data_processamento, '%H:%i') AS minuto,
            COUNT(*) AS total
        FROM streams_processados
        WHERE data_processamento >= NOW() - INTERVAL 30 MINUTE
        GROUP BY minuto
        ORDER BY minuto ASC
    """)
    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)
@app.route('/ranking/artistas/<periodo>')
def ranking_artistas_periodo(periodo):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    if periodo == 'hoje':
        filtro = "WHERE DATE(data_processamento) = CURDATE()"
    elif periodo == 'semana':
        filtro = "WHERE data_processamento >= NOW() - INTERVAL 7 DAY"
    else:
        filtro = ""

    cursor.execute(f"""
        SELECT
            artista,
            COUNT(*) AS total
        FROM streams_processados
        {filtro}
        GROUP BY artista
        ORDER BY total DESC
        LIMIT 5
    """)

    lista = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(lista)

app.run(port=5000)