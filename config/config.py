import json
import os

# Chemin vers le fichier credentials.json
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'credentials.json')

# Chargement du JSON
def load_config():
    with open(CREDENTIALS_PATH, 'r') as f:
        return json.load(f)

# Objet config global
config = load_config()

# Fonction utilitaire pour accéder aux secrets
def get_secret(key, default=None):
    value = config.get(key, default)
    if value is None:
        raise ValueError(f"⚠️ Secret '{key}' manquant dans credentials.json")
    return value