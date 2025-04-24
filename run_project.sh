#!/bin/bash

echo "🔧 Activation de l'environnement virtuel..."
source .venv/bin/activate

echo "🐳 Lancement de Docker Compose..."
docker compose up -d

echo "⏳ Attente du démarrage de MongoDB..."
sleep 5  # Ajuste si nécessaire

echo "🚀 Lancement du script principal..."
python main.py