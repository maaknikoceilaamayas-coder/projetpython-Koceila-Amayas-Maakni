# test_structure.py
"""
Test de la structure du projet
"""
import sys
import os

def test_imports():
    """Teste que tous les modules s'importent correctement"""
    print("Test de la structure du projet...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_path)
    
    print(f"Dossier courant: {current_dir}")
    print(f"Chemin src: {src_path}")
    
    tests_passed = 0
    total_tests = 4
    
    try:
        from settings import BASE_URL, HEADERS, DATA_DIR
        print("settings.py - IMPORT REUSSI")
        print(f"   BASE_URL: {BASE_URL}")
        print(f"   DATA_DIR: {DATA_DIR}")
        tests_passed += 1
        
    except ImportError as e:
        print(f"settings.py - ECHEC: {e}")
    
    try:
        from utils import ensure_dir, write_csv
        print("utils.py - IMPORT REUSSI")
        tests_passed += 1
        
        ensure_dir("test_temp")
        if os.path.exists("test_temp"):
            os.rmdir("test_temp")
            print("Fonction ensure_dir() testee")
        
    except ImportError as e:
        print(f"utils.py - ECHEC: {e}")
    except Exception as e:
        print(f"utils.py - ERREUR: {e}")
    
    try:
        from parsers import get_category_links, parse_product_page
        print("parsers.py - IMPORT REUSSI")
        tests_passed += 1
        
    except ImportError as e:
        print(f"parsers.py - ECHEC: {e}")
    
    try:
        from scrape import main
        print("scrape.py - IMPORT REUSSI")
        tests_passed += 1
        
    except ImportError as e:
        print(f"scrape.py - ECHEC: {e}")
    
    print("=" * 50)
    if tests_passed == total_tests:
        print(f"SUCCES: {tests_passed}/{total_tests} testes passes")
        print("La structure est correcte!")
    else:
        print(f"ATTENTION: {tests_passed}/{total_tests} testes passes")
        print("Il y a des problemes d'import")
    
    print("=" * 50)

if __name__ == "__main__":
    test_imports()