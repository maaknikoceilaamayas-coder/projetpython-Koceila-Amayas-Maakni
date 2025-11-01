# src/parsers.py
"""
Fonctions de parsing HTML pour le scraper
"""
import requests
from bs4 import BeautifulSoup
import time

try:
    from settings import BASE_URL, HEADERS, TIMEOUT, SELECTORS, DEFAULT_MAX_PAGES
    from utils import clean_filename, format_price, rating_to_stars
except ImportError:
    from .settings import BASE_URL, HEADERS, TIMEOUT, SELECTORS, DEFAULT_MAX_PAGES
    from .utils import clean_filename, format_price, rating_to_stars

def get_soup(url):
    """
    Recupere et parse une page HTML
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Erreur lors du chargement de {url}: {e}")
        return None

def get_category_links(main_url=BASE_URL):
    """
    Recupere tous les liens de categories depuis la page d'accueil
    """
    print("Extraction des liens de categories...")
    soup = get_soup(main_url)
    category_links = []
    
    if soup:
        try:
            categories_section = soup.find('ul', class_='nav nav-list')
            if categories_section:
                links = categories_section.find_all('a')
                for link in links[1:]:
                    href = link['href']
                    full_url = BASE_URL + href
                    category_name = link.text.strip()
                    category_links.append({
                        'url': full_url,
                        'name': category_name
                    })
                    print(f"  {category_name}")
        except Exception as e:
            print(f"Erreur lors de l'extraction des categories: {e}")
    
    print(f"{len(category_links)} categories trouvees")
    return category_links

def parse_list_page(list_url, category_name):
    """
    Parse une page liste de livres et extrait les URLs des livres
    """
    print(f"  Parsing page liste: {list_url}")
    soup = get_soup(list_url)
    book_urls = []
    next_page_url = None
    
    if soup:
        try:
            book_containers = soup.select(SELECTORS['book_containers'])
            
            for container in book_containers:
                link = container.find('h3').find('a') if container.find('h3') else None
                if link and link.get('href'):
                    book_href = link['href']
                    if book_href.startswith('../../../'):
                        book_url = book_href.replace('../../../', BASE_URL + 'catalogue/')
                    elif book_href.startswith('../../..'):
                        book_url = book_href.replace('../../..', BASE_URL)
                    else:
                        book_url = BASE_URL + 'catalogue/' + book_href.replace('../', '')
                    
                    book_urls.append(book_url)
            
            next_link = soup.select_one(SELECTORS['next_page'])
            if next_link and next_link.get('href'):
                next_href = next_link['href']
                if list_url.endswith('index.html'):
                    next_page_url = list_url.replace('index.html', next_href)
                else:
                    base_url = '/'.join(list_url.split('/')[:-1]) + '/'
                    next_page_url = base_url + next_href
            
        except Exception as e:
            print(f"Erreur lors du parsing de la page liste: {e}")
    
    print(f"  {len(book_urls)} livres trouves sur cette page")
    return book_urls, next_page_url

def parse_product_page(product_url, category_name):
    """
    Parse une page detail d'un livre et extrait les informations
    """
    print(f"    Parsing livre: {product_url}")
    soup = get_soup(product_url)
    book_data = {}
    
    if not soup:
        return None
    
    try:
        title_elem = soup.find('h1')
        book_data['title'] = title_elem.text.strip() if title_elem else 'Titre non trouve'
        
        price_elem = soup.find('p', class_='price_color')
        book_data['price'] = format_price(price_elem.text) if price_elem else 0.0
        
        availability_elem = soup.find('p', class_='instock')
        book_data['availability'] = availability_elem.text.strip() if availability_elem else 'Non disponible'
        
        rating_elem = soup.find('p', class_='star-rating')
        rating_class = ' '.join(rating_elem['class']) if rating_elem else ''
        book_data['rating'] = rating_to_stars(rating_class)
        
        description_elem = soup.find('div', id='product_description')
        if description_elem:
            description_parent = description_elem.find_next_sibling('p')
            book_data['description'] = description_parent.text.strip() if description_parent else 'Pas de description'
        else:
            book_data['description'] = 'Pas de description'
        
        image_elem = soup.find('div', class_='item').find('img') if soup.find('div', class_='item') else None
        if image_elem and image_elem.get('src'):
            image_src = image_elem['src']
            if image_src.startswith('../../'):
                book_data['image_url'] = BASE_URL + image_src.replace('../../', '')
            else:
                book_data['image_url'] = BASE_URL + image_src
        
        book_data['category'] = category_name
        book_data['product_url'] = product_url
        
        print(f"    '{book_data['title']}' - £{book_data['price']}")
        
    except Exception as e:
        print(f"Erreur lors du parsing du livre {product_url}: {e}")
        return None
    
    return book_data