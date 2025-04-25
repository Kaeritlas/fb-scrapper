from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from utils.logger import setup_logger

from bs4 import BeautifulSoup
from bs4.element import Tag

from typing import List
import random
import time


#Déclaration d'une classe nommée FacebookScraper. Elle regroupe toutes les fonctionnalités liées au scraping de Facebook (connexion, extraction, etc.).
class FacebookScraper:
    def __init__(self, email: str, password: str, headless: bool):
        self.logger = setup_logger(__name__)
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = self._init_driver()
        
    
    def _init_driver(self):
        """Initialise le navigateur Chrome avec des options anti-bot"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        if self.headless:
            options.add_argument("--headless=new")  # headless "new" pour les versions récentes de Chrome

        #Désactiver les notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2  # 2 = Bloquer
        }
        
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.logger.info("Navigateur Chrome initialisé avec succès.")
        
        return driver
    
    def _simulate_human_typing(self, element:str, text:str):
        """Simulate human-like typing patterns"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.7))
                
    def _accept_cookies(self):
        """Clique sur le bouton 'Autoriser tous les cookies' si présent."""
        try:
            buttons = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            for btn in buttons:
                if btn.text.strip() == "Autoriser tous les cookies":
                    self.driver.execute_script("arguments[0].click();", btn)
                    self.logger.info("✅ Bouton 'Autoriser tous les cookies' cliqué.")
                    time.sleep(2)
                    return
            self.logger.warning("❌ Bouton 'Autoriser tous les cookies' non trouvé.")
        except Exception as e:
            self.logger.exception("❌ Erreur lors de la gestion des cookies :")
        
    def login(self):
        """Login to Facebook"""
        try:
            self.driver.get("https://www.facebook.com/login")
            self.logger.info("🔐 Navigation vers la page de connexion Facebook.")
            #On accepte les cookies
            self._accept_cookies()
            
            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self._simulate_human_typing(email_input, self.email)
            
            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "pass"))
            )
            self._simulate_human_typing(password_input, self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            ActionChains(self.driver)\
                .move_to_element(login_button)\
                .pause(random.uniform(0.2, 0.4))\
                .click()\
                .perform()
            
            self.logger.info("✅ Connexion réussie à Facebook.")
            
            time.sleep(10)
        except Exception as e:
            self.logger.exception("❌ Erreur lors de la connexion à Facebook :")
    
    def go_to_search(self, query:str):
        try:
            """Navigue vers la page de recherche Facebook pour un mot-clé donné."""
            search_url = f"https://www.facebook.com/search/posts/?q={query.replace(' ', '%20')}"
            self.driver.get(search_url)
            self.logger.info(f"🔍 Navigation vers : {search_url}")
            time.sleep(5)  # Attente du chargement initial
        except Exception as e:
            self.logger.exception("❌ Erreur lors de la navigation vers la page de recherche :")
            
    def expand_all_see_more(self):
        """Clique sur tous les boutons 'En voir plus' pour afficher le texte complet des posts."""
        try:
            buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(., 'En voir plus')]")
            self.logger.info(f"🔎 {len(buttons)} boutons 'En voir plus' trouvés")
            for btn in buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"⚠️ Impossible de cliquer sur un bouton : {e}")
        except Exception as e:
            self.logger.warning(f"❌ Erreur lors de la recherche des boutons 'En voir plus' : {e}")
            
    def scroll_to_bottom(self, steps: int, step_size: int, delay: float):
        """
        Simule un défilement progressif vers le bas de la page, en plusieurs étapes.
        Chaque étape descend de 'step_size' pixels, avec une pause 'delay' entre chaque.

        Args:
            steps (int): Nombre de scrolls à effectuer.
            step_size (int): Taille de chaque scroll (en pixels).
            delay (float): Pause entre chaque scroll (en secondes).
        """
        try:
            for i in range(steps):
                self.driver.execute_script(f"window.scrollBy(0, {step_size});")
                #self.logger.info(f"⬇️ Scroll étape {i+1}/{steps} ({step_size}px)")
                time.sleep(delay)
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur lors du scroll progressif : {e}")

            
    def prepare_html_with_scrolls(self, scrolls: int) -> str:
        """Effectue plusieurs cycles de clics sur 'En voir plus' + scroll pour charger un maximum de contenu"""
        try:
            for i in range(scrolls):
                self.logger.info(f"🔁 Scroll cycle {i+1}/{scrolls}")

                # Étape 1 : Cliquer sur les boutons "En voir plus"
                self.expand_all_see_more()
                
                time.sleep(2)
                    
                # Étape 2 : Scroller en bas de page
                self.scroll_to_bottom(steps = 10, step_size = 50, delay = 0.5)
                
                time.sleep(3)

            # 🔁 Retourne le HTML complet après interaction
            self.logger.info("✅ code HTML récupéré :")
            return self.driver.page_source
        
        except Exception as e:
            self.logger.exception("❌ Erreur dans prepare_html_with_scrolls :")
            return ""

        
    
