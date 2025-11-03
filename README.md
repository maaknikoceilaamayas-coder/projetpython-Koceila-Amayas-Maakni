
# Scraper de Livres - Books to Scrape

## Objectif du Projet

Ce projet a pour objectif de développer un scraper web en Python capable d'extraire des données de livres depuis le site Books to Scrape. Le contexte est celui d'un projet éducatif pour apprendre les techniques de web scraping, l'organisation de code Python et la création d'interfaces en ligne de commande.

## Installation des Dépendances

Commande
pip install -r requirements.txt

Comment Exécuter le Scraper
Commande de base :
python run_scraper.py

Pour voir les catégories disponibles :
python run_scraper.py --list-categories

Pour scraper une catégorie spécifique :
python run_scraper.py --category travel

Pour scraper toutes les catégories :
python run_scraper.py --all

Exemples de Commandes
Scraper seulement la catégorie Travel :
python run_scraper.py --category travel

Scraper plusieurs catégories avec un délai :
python run_scraper.py --categories travel mystery --delay 2

Scraper avec limitation de pages pour tester rapidement :
python run_scraper.py --categories poetry --max-pages 1

Scraper toutes les catégories avec un dossier de sortie personnalisé :
python run_scraper.py --all --outdir mes_donnees

