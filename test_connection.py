import os
from pymongo import MongoClient

# Lese die Umgebungsvariable für den MongoDB URI
mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Überprüfen, ob die Verbindung funktioniert
    client.admin.command('ping')
    print("Verbindung zu MongoDB erfolgreich!")
except Exception as e:
    print(f"Fehler bei der Verbindung zu MongoDB: {e}")
