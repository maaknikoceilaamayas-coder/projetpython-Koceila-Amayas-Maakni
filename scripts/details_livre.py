# scripts/details_livre.py - Extraire les details d'un livre
import requests
from selectorlib import Extractor
from urllib.parse import urljoin

def obtenir_details_livre(url_livre):
    """Recupere les details d'un livre"""
    print("Analyse du livre : " + url_livre)
    
    # S'assurer que l'URL est complete
    if not url_livre.startswith('http'):
        url_livre = urljoin('https://books.toscrape.com/catalogue/', url_livre)
    
    response = requests.get(url_livre)
    
    extracteur = Extractor.from_yaml_string("""
    titre:
        css: div.product_main h1
        type: Text
    prix:
        css: p.price_color
        type: Text
    disponibilite:
        css: p.instock.availability
        type: Text
    note:
        css: p.star-rating
        type: Attribute
        attribute: class
    upc:
        css: table.table.table-striped tr:nth-child(1) td
        type: Text
    url_image:
        css: div.item.active img
        type: Attribute
        attribute: src
    """)
    
    donnees_livre = extracteur.extract(response.text)
    
    # Nettoyer les donnees
    if donnees_livre['note']:
        # Extraire le nombre d'etoiles
        rating_class = donnees_livre['note']
        if 'One' in rating_class:
            donnees_livre['note'] = 1
        elif 'Two' in rating_class:
            donnees_livre['note'] = 2
        elif 'Three' in rating_class:
            donnees_livre['note'] = 3
        elif 'Four' in rating_class:
            donnees_livre['note'] = 4
        elif 'Five' in rating_class:
            donnees_livre['note'] = 5
        else:
            donnees_livre['note'] = 0
    
    # Completer l'URL de l'image
    if donnees_livre['url_image']:
        donnees_livre['url_image'] = urljoin('https://books.toscrape.com/', donnees_livre['url_image'])
    
    return donnees_livre

# Test de la fonction
if __name__ == "__main__":
    test_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    book_details = obtenir_details_livre(test_url)
    print("Details du livre :")
    for key, value in book_details.items():
        print("   " + key + ": " + str(value))