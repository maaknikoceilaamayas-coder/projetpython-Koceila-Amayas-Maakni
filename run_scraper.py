# run_scraper.py
"""
Point d'entree simplifie pour le scraper
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrape import main

if __name__ == "__main__":
    main()