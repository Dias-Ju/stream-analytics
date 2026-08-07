@echo off
cd /d "%~dp0"

echo Subindo MySQL...
net start mysql80

echo Subindo Kafka...
docker compose up -d

echo Aguardando Kafka iniciar...
timeout /t 10 /nobreak

echo Subindo API...
start cmd /k "python api.py"

echo Subindo Consumer...
start cmd /k "python consumer.py"

echo Subindo Producer...
start cmd /k "python producer.py"

echo Tudo pronto! Abra o frontend/index.html no navegador.
pause