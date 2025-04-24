# main.py
from selenium_scraper.scraper import FacebookScraper
from selenium_scraper.parser import FacebookParser
from selenium_scraper.model import PostModel
from storage.mongo_client import MongoDBClient
from utils.logger import setup_logger

from pprint import pprint
import time

logger = setup_logger(__name__)

def main():
    # 1. Initialisation du scraper avec les identifiants (à sécuriser dans credentials.json ou .env dans la vraie vie)
    scraper = FacebookScraper(email="horokaeri@gmail.com", password="p4#ZrdSiC8\\Z=2Q", headless=False)

    # 2. Connexion à Facebook
    scraper.login()

    # 3. Rechercher un sujet
    """Pour laisser l'utilisateur choisir le sujet de recherche"""
    #query = input("🔍 Entrez le sujet à rechercher sur Facebook : ")
    
    scraper.go_to_search('Jacques Chirac')
    
    #On laisse le temps à la page de charger complètement
    time.sleep(10)

    # 4. Préparation HTML (clics + scrolls pour charger plus de contenu)
    scraper.prepare_html_with_scrolls(scrolls=5)
    
    # 5. Récupération du HTML complet de la page
    html = scraper.driver.page_source
    
    # 6. Parser le HTML et extraire les posts
    parser = FacebookParser(html)
    parsed_posts = parser.parse_all()

    # 7. Affichage formaté des résultats
    for post in parsed_posts:
        logger.debug(post)  # Grâce à __repr__

        
    # 8. Conversion en objets PostModel
    post_models = [post for post in parsed_posts if post.is_valid()]

    # 9. Sauvegarde dans MongoDB
    mongo = MongoDBClient()
    mongo.insert_many_posts(post_models)
    
if __name__ == "__main__":
    main()