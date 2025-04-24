
# 📘 Facebook Post Scraper

Un projet de scraping web en Python conçu pour extraire des posts publics depuis Facebook à l’aide de Selenium et BeautifulSoup, puis les stocker dans une base MongoDB.

---

## 🗂️ Structure du projet

```
fb_scraper/
├── main.py                      # Script principal à exécuter
├── config/
│   └── config.py
├── data/
│   └──credentials.json         # Gestion des secrets via credentials.json
├── selenium_scraper/
│   ├── scraper.py              # Classe FacebookScraper (connexion + navigation + scrolling)
│   ├── parser.py               # Classe FacebookParser (nettoyage des données HTML)
│   └── model.py                # Classe PostModel (structure des données)
├── storage/
│   └── mongo_client.py         # Connexion MongoDB + insertion + index
├── utils/
│   └── logger.py               # Logger python
├── docker-compose.yml          # Docker compose pour le lancement de la base MongoDB
├── requirements.txt            # Dépendances Python du projet
└── run_project.sh              # Script pour tout lancer automatiquement
```
INSTALLATION DES DÉPENDANCES

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
---

## 🧠 Classes principales

### `FacebookScraper`

Classe responsable de :
- Connexion à Facebook
- Navigation vers la recherche d’un sujet
- Scroll de la page
- Déclenchement des clics sur “En voir plus”
- Récupération de l’HTML complet (avec tous les posts visibles)

### `FacebookParser`

Classe responsable du parsing :
- Extraction de :
  - `page_name` (nom de la page Facebook)
  - `text` (texte du post)
  - `images` (liste d’URLs d’images)
  - `comments` (nombre de commentaires, convertis même si abrégés : 3,2 K → 3200)
  - `shares` (nombre de partages)

### `PostModel`

Classe légère représentant un post Facebook :
- Valide les données (`is_valid`)
- Transforme l’objet en dictionnaire prêt pour MongoDB (`to_dict`)

### `MongoDBClient`
  -Connexion sécurisée à MongoDB (identifiants via get_secret)
  -Sélection de la base de données et de la collection
  -Création d’un index unique (page_name + text) pour éviter les doublons
  -Insertion d’un ou plusieurs documents :
  -insert_post(post) : insère un post (objet ou dictionnaire)
  -insert_many_posts(posts) : insère plusieurs posts en appelant insert_post pour chacun
  -Gestion des erreurs Mongo (connexion, doublons, insertion) avec logs détaillés

---

## 🗺️ Schéma global

```mermaid
graph TD
    A[main.py] --> B[FacebookScraper]
    B --> C[HTML complet]
    C --> D[FacebookParser]
    D --> E[PostModel]
    E --> F[mongo_client.py]
```

---

## 🔁 Fonctionnement du script

Lorsque tu exécutes `main.py` :

1. Le navigateur Chrome s’ouvre et se connecte à Facebook avec les identifiants de `credentials.json`.
2. L’utilisateur entre un mot-clé dans le terminal.
3. Le scraper :
   - Navigue vers la recherche Facebook pour ce mot
   - Clique sur “En voir plus”
   - Scrolle plusieurs fois
4. Le parser analyse tous les blocs HTML des posts visibles.
5. Les données sont nettoyées et transformées en objets `PostModel`.
6. Les données sont insérées dans MongoDB avec gestion des doublons.

---

## ▶️ Lancer le projet

```bash
chmod +x start_project.sh
./start_project.sh
```

Ce script :
- Active l’environnement virtuel
- Démarre MongoDB via Docker
- Lance `main.py` automatiquement

---

## ✅ Prérequis

- Google Chrome installé
- [ChromeDriver](https://chromedriver.chromium.org/downloads) compatible
- Python 3.10+
- Clé d’accès dans `credentials.json` :
```json
{
  "FB_EMAIL": "ton@email.com",
  "FB_PASSWORD": "motdepasse",
  "MONGO_USER": "user",
  "MONGO_PASSWORD": "motdepasse",
  "MONGO_HOST": "localhost",
  "MONGO_PORT": 27017
}
```
Accéder à la base mongoDB :
  Pour accéder à la base mongoDB utiliser `mongodb://root:example@localhost:27017/` dans un navigateur pour accéder à MongoDB Compass une interface pour visualiser les bases mongoDB (les données ont été refresh avant le dépôt)
---
## 📌 Points à améliorer
- Création de test unitaire pour valider les méthodes des différentes classes de manière isolée
- Analyser le comportement du bot sur les pages facebook pour améliorer le comportement, récolté plus de données et évité la détection du bot
