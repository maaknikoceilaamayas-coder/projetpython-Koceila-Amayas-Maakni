# src/settings.py
"""
Configuration et constantes pour le scraper de livres
"""

# URLs et configuration de base
BASE_URL = "http://books.toscrape.com/"
CATALOGUE_URL = "http://books.toscrape.com/catalogue/"

# Headers pour les requêtes HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# Configuration du scraping
DEFAULT_DELAY = 1
TIMEOUT = 10
MAX_RETRIES = 3
DEFAULT_MAX_PAGES = None

# Chemins des dossiers
DATA_DIR = "data"
IMAGES_DIR = "images"
OUTPUTS_DIR = "outputs"
DEFAULT_OUTDIR = "outputs"

# Configuration CSV
CSV_ENCODING = "utf-8"
CSV_FIELDNAMES = ['title', 'price', 'availability', 'rating', 'description', 'image_url', 'category']

# Sélecteurs CSS
SELECTORS = {
    'book_containers': 'article.product_pod',
    'title': 'h3 a',
    'price': 'p.price_color',
    'availability': 'p.instock',
    'rating': 'p.star-rating',
    'next_page': 'li.next a'
}