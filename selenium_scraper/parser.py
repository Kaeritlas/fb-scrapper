from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag
from selenium_scraper.model import PostModel
import re

from utils.logger import setup_logger

"""
Classe qui transforme les balises HTML d’un post Facebook (BeautifulSoup) en dictionnaires structurés prêts à être insérés dans une base de données
"""

class FacebookParser:
    def __init__(self, html: str):
        """Initialise le parser avec la page HTML brute (Facebook search page)."""
        self.logger = setup_logger(__name__)
        self.soup = BeautifulSoup(html, "html.parser")

    def parse_all(self) -> List[PostModel]:
        """Extrait tous les posts présents dans la page HTML."""
        try:
            post_divs = self.soup.find_all("div", {"class": "x1n2onr6 x1ja2u2z"})
            self.logger.info(f"{len(post_divs)} blocs de post trouvés.")
        except Exception as e:
            self.logger.exception("Erreur lors de la recherche des blocs de post.")
            return []

        parsed_posts = []
        for post_div in post_divs:
            try:
                parsed_dict = self._parse_single_post(post_div)
                post = PostModel(**parsed_dict)
                if post.is_valid():
                    parsed_posts.append(post)
                else:
                    self.logger.warning(f"Post {post_div} ignoré : données incomplètes.")
            except Exception as e:
                self.logger.exception(f"Erreur lors du parsing du post {post_div}")
        return parsed_posts
    
    def _parse_single_post(self, post_div: Tag) -> Dict:
        """Extrait toutes les informations d'un seul post HTML"""
        return {
            "page_name": self._extract_page_name(post_div),
            "text": self._extract_text(post_div),
            "images": self._extract_images(post_div),
            "comments": self._extract_comment_count(post_div),
            "shares": self._extract_share_count(post_div)
        }

    def _extract_page_name(self, post_div: Tag) -> str:
        """Récupère le nom de la page Facebook ayant publié le post"""
        try:
            page_div = post_div.find("div", {"data-ad-rendering-role": "profile_name"})
            if page_div:
                span = page_div.find("span")
                while span and span.find("span"):
                    span = span.find("span")
                if span:
                    return span.get_text(strip=True)
        except Exception:
            self.logger.warning("Impossible d'extraire le nom de la page.")
        return None

    def _extract_text(self, post_div: Tag) -> str:
        """Récupère le texte principal du post"""
        try:
            message = post_div.find("div", {"data-ad-preview": "message"})
            return message.get_text(strip=True) if message else None
        except Exception:
            self.logger.warning("Erreur lors de l'extraction du texte.")
            return None

    def _extract_images(self, post_div: Tag) -> List[str]:
        """Récupère les URLs d’images du post et on filtre les stickers, emojis, et images inline (base64)"""
        image_urls = []
        try:
            for img in post_div.find_all("img"):
                src = img.get("src", "")
                if (
                    src.startswith("http")
                    and "fbcdn.net" in src
                    and "emoji.php" not in src
                    and "sticker" not in src
                    and not src.startswith("data:image")
                ):
                    image_urls.append(src)
        except Exception:
            self.logger.warning("Erreur lors de l'extraction des images.")
            
        return image_urls

    def _extract_comment_count(self, post_div: Tag) -> int:
        """Récupère le nombre de commentaires (entier) d’un post"""
        return self._extract_number(post_div, keyword="commentaire")

    def _extract_share_count(self, post_div: Tag) -> int:
        """Récupère le nombre de partages (entier) d’un post"""
        return self._extract_number(post_div, keyword="partage")

    def _extract_number(self, post_div: Tag, keyword: str) -> int:
        """Extrait un nombre à partir d’un mot-clé (commentaire ou partage)"""
        try:
            for span in post_div.find_all("span"):
                text = span.get_text(" ", strip=True).lower()
                text = text.replace("\xa0", " ").replace("&nbsp;", " ")
                
                # Évite les boutons "commenter" ou textes sans chiffres
                if keyword in text and keyword + "s" in text and any(char.isdigit() for char in text):
                    if not any(bad in text for bad in ["commenter", "partager"]):
                        self.logger.debug(f"[{keyword}] ➕ Match trouvé dans : '{text}'")
                        return self._parse_number(text)

            self.logger.debug(f"[{keyword}] ❌ Aucun span correspondant trouvé dans ce post.")
            return None

        except Exception as e:
            self.logger.warning(f"[{keyword}] ⚠️ Erreur lors de l'extraction : {e}")
            return None

    def _parse_number(self, text: str) -> int:
        """Convertit un texte avec des formats abrégés (K, M) en entier | Exemple : "3,2 K commentaires" → 3200"""
        try:
            match = re.search(r"(\d+(?:[.,]\d+)?)(?:\s*([km]))?", text.lower())
            if not match:
                self.logger.debug(f"🔎 Aucun nombre détecté dans : '{text}'")
                return None

            number = float(match.group(1).replace(",", "."))
            suffix = match.group(2)

            if suffix == "k":
                number *= 1_000
            elif suffix == "m":
                number *= 1_000_000
                
            final_number = int(number)
            self.logger.debug(f"✅ Nombre extrait : {final_number} à partir de '{text}'")
            return int(number)
        except Exception:
            self.logger.warning(f"Erreur lors du parsing du nombre : '{text}'")
            return None