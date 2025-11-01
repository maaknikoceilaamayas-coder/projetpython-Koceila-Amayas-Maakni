# scraper_books.py - Projet de scraping
import requests
import csv
import os
import time

def get_book_details(book_url):
    """Recupere les details d'un livre depuis sa page"""
    print("Extraction du livre: " + book_url)
    
    try:
        response = requests.get(book_url)
        if response.status_code != 200:
            print("Erreur pour acceder a la page: " + str(response.status_code))
            return None
    except Exception as e:
        print("Probleme de connexion: " + str(e))
        return None
    
    # Extraire les informations manuellement
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    book_data = {}
    
    # Titre
    title_element = soup.find('h1')
    if title_element:
        book_data['titre'] = title_element.text.strip()
    
    # Prix
    price_element = soup.find('p', class_='price_color')
    if price_element:
        book_data['prix'] = price_element.text.strip()
    
    # Disponibilite
    availability_element = soup.find('p', class_='instock')
    if availability_element:
        book_data['disponibilite'] = availability_element.text.strip()
    
    # Note
    rating_element = soup.find('p', class_='star-rating')
    if rating_element:
        rating_class = rating_element.get('class', [])
        if 'One' in rating_class:
            book_data['note'] = 1
        elif 'Two' in rating_class:
            book_data['note'] = 2
        elif 'Three' in rating_class:
            book_data['note'] = 3
        elif 'Four' in rating_class:
            book_data['note'] = 4
        elif 'Five' in rating_class:
            book_data['note'] = 5
        else:
            book_data['note'] = 0
    
    # UPC
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            header = row.find('th')
            if header and header.text == 'UPC':
                value = row.find('td')
                if value:
                    book_data['upc'] = value.text
    
    # Image
    image_element = soup.find('img')
    if image_element:
        image_url = image_element.get('src', '')
        if image_url:
            # Corriger l'URL de l'image
            if image_url.startswith('../../../'):
                image_url = image_url.replace('../../../', '')
            book_data['url_image'] = 'https://books.toscrape.com/' + image_url
    
    return book_data

def fix_book_url(book_link, current_page_url):
    """Corrige l'URL du livre"""
    if book_link.startswith('http'):
        return book_link
    
    # Si le lien commence par ../../
    if book_link.startswith('../../../'):
        # Enlever les ../
        clean_link = book_link.replace('../../../', '')
        return 'https://books.toscrape.com/catalogue/' + clean_link
    
    # Si c'est un lien relatif simple
    if book_link.startswith('../'):
        clean_link = book_link.replace('../', '')
        return 'https://books.toscrape.com/catalogue/' + clean_link
    
    # Pour les autres cas
    base_url = 'https://books.toscrape.com/catalogue/'
    if not book_link.startswith('catalogue/'):
        return base_url + book_link
    else:
        return 'https://books.toscrape.com/' + book_link

def scrape_category(category_url, category_name):
    """Scrape tous les livres d'une categorie"""
    print("Scraping de la categorie: " + category_name)
    
    all_books = []
    current_url = category_url
    page_number = 1
    
    while current_url:
        print("Page " + str(page_number) + ": " + current_url)
        
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                print("Erreur sur la page " + str(page_number))
                break
        except Exception as e:
            print("Probleme de connexion pour la page: " + str(e))
            break
        
        # Parser la page avec BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver tous les livres sur la page
        book_elements = soup.find_all('article', class_='product_pod')
        
        print("Trouve " + str(len(book_elements)) + " livres sur cette page")
        
        for i, book_element in enumerate(book_elements):
            # Trouver le lien du livre
            link_element = book_element.find('h3').find('a')
            if link_element:
                book_link = link_element.get('href', '')
                if book_link:
                    # Corriger l'URL du livre
                    fixed_book_url = fix_book_url(book_link, current_url)
                    print("Livre " + str(i+1) + ": " + fixed_book_url)
                    
                    # Recuperer les details du livre
                    book_details = get_book_details(fixed_book_url)
                    
                    if book_details:
                        # Ajouter la categorie
                        book_details['categorie'] = category_name
                        all_books.append(book_details)
                        print("Succes pour le livre: " + book_details['titre'][:30])
                    else:
                        print("Echec pour le livre " + str(i+1))
                    
                    # Attendre un peu entre les livres
                    time.sleep(0.3)
        
        # Verifier s'il y a une page suivante
        next_button = soup.find('li', class_='next')
        if next_button:
            next_link = next_button.find('a')
            if next_link:
                # Construire l'URL de la page suivante
                next_url = next_link.get('href')
                if current_url.endswith('index.html'):
                    base_url = current_url.replace('index.html', '')
                    current_url = base_url + next_url
                else:
                    # Pour les pages 2, 3, etc.
                    base_url = current_url.rsplit('/', 1)[0] + '/'
                    current_url = base_url + next_url
                page_number += 1
            else:
                current_url = None
        else:
            current_url = None
    
    return all_books

def get_all_categories():
    """Recupere la liste de toutes les categories"""
    url = "https://books.toscrape.com/"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Impossible d'acceder au site")
            return []
    except Exception as e:
        print("Erreur de connexion: " + str(e))
        return []
    
    # Parser la page d'accueil
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    categories = []
    
    # Trouver la sidebar avec les categories
    sidebar = soup.find('div', class_='side_categories')
    if sidebar:
        category_links = sidebar.find_all('a')
        for link in category_links:
            # Ignorer le lien "Books" principal
            if link.text.strip() != 'Books':
                category_url = 'https://books.toscrape.com/' + link.get('href')
                category_name = link.text.strip()
                # Creer un slug simple pour le nom de fichier
                category_slug = category_name.lower().replace(' ', '_')
                
                categories.append({
                    'nom': category_name,
                    'url': category_url,
                    'slug': category_slug
                })
    
    return categories

def save_to_csv(books, category_name):
    """Sauvegarde les livres dans un fichier CSV"""
    if not books:
        print("Aucun livre a sauvegarder pour " + category_name)
        return False
    
    # Creer le dossier si besoin
    if not os.path.exists('donnees'):
        os.makedirs('donnees')
    
    filename = 'donnees/' + category_name + '.csv'
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            # Utiliser les cles du premier livre comme colonnes
            fieldnames = books[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            writer.writeheader()
            for book in books:
                writer.writerow(book)
        
        print(str(len(books)) + " livres sauvegardes dans: " + filename)
        return True
    except Exception as e:
        print("Erreur lors de la sauvegarde: " + str(e))
        return False

def download_images(books, category_name):
    """Telecharge les images des livres"""
    if not books:
        return
    
    print("Telechargement des images pour " + category_name)
    
    # Creer le dossier pour les images
    image_folder = 'images/' + category_name
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    
    count = 0
    for book in books:
        if 'url_image' in book and 'titre' in book:
            try:
                # Creer un nom de fichier simple
                safe_title = ''.join(c for c in book['titre'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')[:30]
                
                filename = image_folder + '/' + safe_title + '.jpg'
                
                response = requests.get(book['url_image'])
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    count += 1
                    print("Image telechargee: " + safe_title)
            except Exception as e:
                print("Erreur pour l'image: " + book['titre'][:20])
    
    print(str(count) + " images telechargees")

def main():
    """Fonction principale"""
    print("DEBUT DU SCRAPING")
    print("=================")
    
    # Recuperer les categories
    print("Recuperation des categories...")
    categories = get_all_categories()
    
    if not categories:
        print("Aucune categorie trouvee, utilisation de categories de test")
        categories = [
            {'nom': 'Travel', 'url': 'https://books.toscrape.com/catalogue/category/books/travel_2/index.html', 'slug': 'travel'},
            {'nom': 'Mystery', 'url': 'https://books.toscrape.com/catalogue/category/books/mystery_3/index.html', 'slug': 'mystery'}
        ]
    
    print(str(len(categories)) + " categories trouvees")
    for cat in categories:
        print(" - " + cat['nom'])
    
    # Pour le test, on prend seulement 2 categories
    categories_to_scrape = categories[:2]
    
    for category in categories_to_scrape:
        print("\n" + "="*40)
        print("TRAITEMENT: " + category['nom'])
        print("URL: " + category['url'])
        print("="*40)
        
        # Scraper la categorie
        books = scrape_category(category['url'], category['slug'])
        
        if books:
            # Sauvegarder en CSV
            save_to_csv(books, category['slug'])
            
            # Telecharger les images
            download_images(books, category['slug'])
        else:
            print("Aucun livre trouve dans " + category['nom'])
        
        # Pause entre les categories
        time.sleep(1)
    
    print("\n" + "="*40)
    print("SCRAPING TERMINE")
    print("Les donnees sont dans les dossiers 'donnees/' et 'images/'")

if __name__ == "__main__":
    main()