FROM python:3.11-alpine

# Installiere curl und bash (für das Skript und andere notwendige Befehle)
RUN apk update && apk add --no-cache curl bash

WORKDIR /app

# Kopiere die requirements.txt und installiere die Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopiere den Rest des Projekts
COPY . .

# Lade das wait-for-it.sh-Skript herunter und mache es ausführbar
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Führe das init_script.py aus und danach die Flask-App
CMD ["/usr/local/bin/wait-for-it.sh", "mongodb:27017", "--", "python", "/app/init_script.py", "&&", "python", "/app/app.py"]
