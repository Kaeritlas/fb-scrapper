# storage/mongo_client.py

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from urllib.parse import quote_plus
from config.config import get_secret

from utils.logger import setup_logger


class MongoDBClient:
    def __init__(self, db_name="fb_scraper", collection_name="posts"):
        self.logger = setup_logger(__name__)
        self.db_name = db_name
        self.collection_name = collection_name
        
        try:
            self.client = self._connect()
            self.collection = self._get_collection()
            self._ensure_indexes()
            self.logger.info(f"✅ Connexion à MongoDB établie (DB: {db_name}, Collection: {collection_name})")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation de MongoDB : {e}")
            raise
            
    def _connect(self):
        username = quote_plus(get_secret("MONGO_USER"))
        password = quote_plus(get_secret("MONGO_PASSWORD"))
        host = get_secret("MONGO_HOST") or "localhost"
        port = get_secret("MONGO_PORT") or 27017

        uri = f"mongodb://{username}:{password}@{host}:{port}/"
        return MongoClient(uri)

    def _get_collection(self):
        db = self.client[self.db_name]
        return db[self.collection_name]

    def _ensure_indexes(self):
        try :
            self.collection.create_index(
                [("text", 1), ("page_name", 1)],
                unique=True
            )
            self.logger.info("📌 Index unique créé sur ('text', 'page_name')")
        except PyMongoError as e:
            self.logger.warning(f"⚠️ Impossible de créer l'index : {e}")

    def insert_post(self, post):
        if hasattr(post, "to_dict"):
            post = post.to_dict()

        if not isinstance(post, dict):
            self.logger.error("❌ Le document à insérer n'est pas un dictionnaire valide.")
            return

        try:
            self.collection.insert_one(post)
            self.logger.info("✅ Post inséré avec succès.")
        except DuplicateKeyError:
            self.logger.warning("⚠️ Doublon détecté : insertion ignorée.")
        except PyMongoError as e:
            self.logger.error(f"❌ Erreur lors de l'insertion du post : {e}")

    def insert_many_posts(self, posts):
        self.logger.info(f"📥 Insertion de {len(posts)} posts...")
        inserted = 0
        for post in posts:
            before = self.collection.count_documents({})
            self.insert_post(post)
            after = self.collection.count_documents({})
            if after > before:
                inserted += 1
        self.logger.info(f"✅ {inserted} posts insérés avec succès.")
