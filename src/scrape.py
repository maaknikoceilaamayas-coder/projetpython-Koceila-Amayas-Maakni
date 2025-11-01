# src/scrape.py
"""
Script principal du scraper de livres avec CLI avancee
"""
import argparse
import time
import os
import sys

try:
    from settings import BASE_URL, DEFAULT_DELAY, TIMEOUT, DEFAULT_MAX_PAGES, DEFAULT_OUTDIR
    from parsers import get_category_links, parse_list_page, parse_product_page
    from utils import write_csv, download_image, clean_filename, set_output_directory
except ImportError:
    from .settings import BASE_URL, DEFAULT_DELAY, TIMEOUT, DEFAULT_MAX_PAGES, DEFAULT_OUTDIR
    from .parsers import get_category_links, parse_list_page, parse_product_page
    from .utils import write_csv, download_image, clean_filename, set_output_directory

def scrape_category(category_url, category_name, delay=DEFAULT_DELAY, max_pages=DEFAULT_MAX_PAGES):
    """
    Scrape tous les livres d'une categorie avec limite de pages
    """
    print(f"Scraping de la categorie: {category_name}")
    print(f"URL: {category_url}")
    if max_pages:
        print(f"Limite: {max_pages} pages maximum")
    
    all_books = []
    current_page_url = category_url
    page_count = 1
    
    while current_page_url:
        print(f"  Page {page_count}")
        
        book_urls, next_page_url = parse_list_page(current_page_url, category_name)
        
        for book_url in book_urls:
            book_data = parse_product_page(book_url, category_name)
            if book_data:
                all_books.append(book_data)
            
            time.sleep(delay)
        
        current_page_url = next_page_url
        page_count += 1
        
        if max_pages and page_count > max_pages:
            print(f"  Limite de {max_pages} pages atteinte")
            break
            
        if current_page_url:
            time.sleep(delay)
    
    print(f"Categorie '{category_name}' terminee: {len(all_books)} livres scrapes")
    return all_books

def scrape_selected_categories(category_names, delay=DEFAULT_DELAY, max_pages=DEFAULT_MAX_PAGES, output_file=None):
    """
    Scrape seulement les categories specifiees
    """
    categories = get_category_links()
    selected_categories = []
    
    for category_name in category_names:
        found = False
        for category in categories:
            if category['name'].lower() == category_name.lower():
                selected_categories.append(category)
                found = True
                break
        if not found:
            print(f"Attention: Categorie '{category_name}' non trouvee")
    
    if not selected_categories:
        print("Aucune categorie valide specifiee")
        available_categories = [cat['name'] for cat in categories]
        print(f"Categories disponibles: {', '.join(available_categories)}")
        return
    
    print(f"Scraping de {len(selected_categories)} categories selectionnees")
    all_books = []
    
    for i, category in enumerate(selected_categories, 1):
        print("=" * 50)
        print(f"Categorie {i}/{len(selected_categories)}: {category['name']}")
        print("=" * 50)
        
        books_data = scrape_category(category['url'], category['name'], delay, max_pages)
        all_books.extend(books_data)
        
        filename = f"{clean_filename(category['name'])}.csv"
        write_csv(books_data, filename)
        
        if i < len(selected_categories):
            print("Attente avant la categorie suivante...")
            time.sleep(delay * 2)
    
    if output_file and all_books:
        print(f"Sauvegarde globale dans {output_file}")
        write_csv(all_books, output_file)
    
    print(f"Scraping termine! {len(all_books)} livres au total")

def scrape_single_category(category_name, delay=DEFAULT_DELAY, max_pages=DEFAULT_MAX_PAGES, output_file=None):
    """
    Scrape une categorie specifique
    """
    categories = get_category_links()
    target_category = None
    
    for category in categories:
        if category['name'].lower() == category_name.lower():
            target_category = category
            break
    
    if not target_category:
        print(f"Categorie '{category_name}' non trouvee")
        available_categories = [cat['name'] for cat in categories]
        print(f"Categories disponibles: {', '.join(available_categories)}")
        return
    
    books_data = scrape_category(target_category['url'], target_category['name'], delay, max_pages)
    
    if books_data:
        filename = output_file or f"{clean_filename(category_name)}.csv"
        write_csv(books_data, filename)
        
        download_images = input("Telecharger les images? (o/n): ").lower().startswith('o')
        if download_images:
            download_category_images(books_data, category_name)
    else:
        print("Aucune donnee a sauvegarder")

def scrape_all_categories(delay=DEFAULT_DELAY, max_pages=DEFAULT_MAX_PAGES):
    """
    Scrape toutes les categories
    """
    print("Demarrage du scraping de toutes les categories")
    
    categories = get_category_links()
    print(f"{len(categories)} categories a scraper")
    
    all_books = []
    
    for i, category in enumerate(categories, 1):
        print("=" * 50)
        print(f"Categorie {i}/{len(categories)}: {category['name']}")
        print("=" * 50)
        
        books_data = scrape_category(category['url'], category['name'], delay, max_pages)
        all_books.extend(books_data)
        
        filename = f"{clean_filename(category['name'])}.csv"
        write_csv(books_data, filename)
        
        if i < len(categories):
            print("Attente avant la categorie suivante...")
            time.sleep(delay * 2)
    
    print("Sauvegarde de tous les livres...")
    write_csv(all_books, "all_books.csv")
    print(f"Scraping termine! {len(all_books)} livres au total")

def download_category_images(books_data, category_name):
    """
    Telecharge les images pour une categorie
    """
    from utils import download_image, clean_filename
    
    print(f"Telechargement des images pour {category_name}...")
    downloaded = 0
    
    for book in books_data:
        if book.get('image_url') and book.get('title'):
            image_name = f"{clean_filename(book['title'])}.jpg"
            if download_image(book['image_url'], image_name):
                downloaded += 1
    
    print(f"{downloaded}/{len(books_data)} images telechargees")

def main():
    """
    Fonction principale avec interface en ligne de commande avancee
    """
    parser = argparse.ArgumentParser(
        description='Scraper de livres Books to Scrape - CLI Avancee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python scrape.py --categories Travel Poetry --max-pages 1
  python scrape.py --categories Travel --delay 2 --outdir my_data
  python scrape.py --all --max-pages 2 --delay 1.5
  python scrape.py --list-categories
  python scrape.py --category travel --output livres_voyage.csv
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=False)
    
    group.add_argument('--category', 
                       help='Scraper une categorie specifique (ex: "travel")')
    
    group.add_argument('--categories', 
                       nargs='+',
                       help='Scraper plusieurs categories (ex: "Travel Poetry Mystery")')
    
    group.add_argument('--all', 
                       action='store_true',
                       help='Scraper toutes les categories')
    
    group.add_argument('--list-categories',
                       action='store_true',
                       help='Lister toutes les categories disponibles')
    
    parser.add_argument('--max-pages', 
                       type=int,
                       default=DEFAULT_MAX_PAGES,
                       help='Limiter le nombre de pages par categorie (defaut: pas de limite)')
    
    parser.add_argument('--delay', 
                       type=float, 
                       default=DEFAULT_DELAY,
                       help=f'Delai entre les requetes en secondes (defaut: {DEFAULT_DELAY})')
    
    parser.add_argument('--outdir', 
                       default=DEFAULT_OUTDIR,
                       help=f'Dossier de sortie personnalise (defaut: {DEFAULT_OUTDIR})')
    
    parser.add_argument('--output', 
                       help='Fichier de sortie personnalise (pour categories individuelles)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SCRAPER DE LIVRES - BOOKS TO SCRAPE - CLI AVANCEE")
    print("=" * 60)
    
    try:
        # Configuration du dossier de sortie
        set_output_directory(args.outdir)
        
        if args.list_categories:
            categories = get_category_links()
            print("Categories disponibles:")
            for cat in categories:
                print(f"  {cat['name']}")
            print(f"Total: {len(categories)} categories")
            
        elif args.category:
            scrape_single_category(args.category, args.delay, args.max_pages, args.output)
            
        elif args.categories:
            scrape_selected_categories(args.categories, args.delay, args.max_pages, args.output)
            
        elif args.all:
            confirm = input("Scraper toutes les categories? Cela peut prendre du temps. (o/n): ")
            if confirm.lower().startswith('o'):
                scrape_all_categories(args.delay, args.max_pages)
            else:
                print("Operation annulee")
                
        else:
            parser.print_help()
            print("Utilisez --list-categories pour voir les categories disponibles")
    
    except KeyboardInterrupt:
        print("Scraping interrompu par l'utilisateur")
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()