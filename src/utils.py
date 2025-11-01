# src/utils.py
"""
Fonctions utilitaires pour le scraper
"""
import os
import csv
import requests
from bs4 import BeautifulSoup

try:
    from settings import DATA_DIR, IMAGES_DIR, OUTPUTS_DIR, HEADERS, CSV_ENCODING, CSV_FIELDNAMES, DEFAULT_OUTDIR
except ImportError:
    from .settings import DATA_DIR, IMAGES_DIR, OUTPUTS_DIR, HEADERS, CSV_ENCODING, CSV_FIELDNAMES, DEFAULT_OUTDIR

def ensure_dir(directory):
    """
    Cree un dossier s'il n'existe pas
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Dossier cree: {directory}")

def set_output_directory(outdir):
    """
    Definit le dossier de sortie pour les fichiers
    """
    global DATA_DIR, IMAGES_DIR, OUTPUTS_DIR
    DATA_DIR = os.path.join(outdir, "data")
    IMAGES_DIR = os.path.join(outdir, "images")
    OUTPUTS_DIR = outdir
    ensure_dir(DATA_DIR)
    ensure_dir(IMAGES_DIR)
    ensure_dir(OUTPUTS_DIR)
    print(f"Dossier de sortie defini: {outdir}")

def write_csv(data, filename):
    """
    Ecrit des donnees dans un fichier CSV
    """
    ensure_dir(DATA_DIR)
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        if data and len(data) > 0:
            with open(filepath, 'w', newline='', encoding=CSV_ENCODING) as file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"Donnees sauvegardees dans {filepath} ({len(data)} enregistrements)")
            return True
        else:
            print("Aucune donnee a sauvegarder")
            return False
    except Exception as e:
        print(f"Erreur lors de l'ecriture du CSV: {e}")
        return False

def download_image(image_url, image_name):
    """
    Telecharge une image depuis une URL
    """
    ensure_dir(IMAGES_DIR)
    filepath = os.path.join(IMAGES_DIR, image_name)
    
    try:
        response = requests.get(image_url, headers=HEADERS)
        response.raise_for_status()
        
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Image telechargee: {image_name}")
        return True
    except Exception as e:
        print(f"Erreur telechargement image {image_name}: {e}")
        return False

def clean_filename(filename):
    """
    Nettoie un nom de fichier des caracteres invalides
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = filename.strip()[:100]
    return filename

def format_price(price_text):
    """
    Formate le prix pour en extraire la valeur numerique
    """
    try:
        return float(price_text.replace('£', '').strip())
    except (ValueError, AttributeError):
        return 0.0

def rating_to_stars(rating_class):
    """
    Convertit une classe de rating en nombre d'etoiles
    """
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    for key, value in rating_map.items():
        if key in rating_class:
            return value
    return 0