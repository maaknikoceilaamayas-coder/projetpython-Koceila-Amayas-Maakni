# analyser_donnees.py
"""
Script pour analyser les données scrapées
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob

def analyser_categorie(fichier_csv):
    """Analyse une catégorie de livres"""
    print(f"Analyse du fichier : {fichier_csv}")
    
    try:
        df = pd.read_csv(fichier_csv)
        
        print(f"Nombre de livres : {len(df)}")
        print(f"Prix moyen : £{df['price'].mean():.2f}")
        print(f"Rating moyen : {df['rating'].mean():.1f}/5")
        print(f"Prix min/max : £{df['price'].min():.2f} - £{df['price'].max():.2f}")
        
        return df
        
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}")
        return None

def comparer_categories(dossier_data="data"):
    """Compare plusieurs catégories"""
    print("Comparaison des catégories :")
    
    csv_files = glob(os.path.join(dossier_data, "*.csv"))
    results = []
    
    for fichier in csv_files:
        nom_categorie = os.path.basename(fichier).replace('.csv', '')
        df = pd.read_csv(fichier)
        
        results.append({
            'Catégorie': nom_categorie,
            'Livres': len(df),
            'Prix Moyen': df['price'].mean(),
            'Rating Moyen': df['rating'].mean()
        })
    
    results_df = pd.DataFrame(results)
    print(results_df)
    
    return results_df

def main():
    """Fonction principale"""
    print("=== ANALYSE DES DONNEES SCRAPEES ===")
    
    # Analyse des fichiers disponibles
    data_files = glob("data/*.csv")
    if not data_files:
        print("Aucun fichier de données trouvé. Scrapez d'abord des données.")
        return
    
    print("Fichiers disponibles :")
    for i, fichier in enumerate(data_files, 1):
        print(f"  {i}. {os.path.basename(fichier)}")
    
    # Analyser le premier fichier
    if data_files:
        print("\n" + "="*50)
        df = analyser_categorie(data_files[0])
        
        # Comparaison si plusieurs fichiers
        if len(data_files) > 1:
            print("\n" + "="*50)
            comparer_categories()

if __name__ == "__main__":
    main()