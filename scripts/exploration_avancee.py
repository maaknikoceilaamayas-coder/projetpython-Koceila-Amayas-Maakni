# exploration_avancee.py - Analyse complete du dataset (version simplifiee)
import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import Counter
import re

class AnalyseurLivres:
    def __init__(self):
        self.dossier_csv = "outputs/csv"
        self.df_complet = None
        self.charger_donnees()
    
    def charger_donnees(self):
        """Charge tous les fichiers CSV en un seul DataFrame"""
        print("CHARGEMENT DES DONNEES...")
        
        if not os.path.exists(self.dossier_csv):
            print("Dossier outputs/csv/ non trouve")
            return
        
        fichiers = [f for f in os.listdir(self.dossier_csv) if f.endswith('.csv')]
        
        if not fichiers:
            print("Aucun fichier CSV trouve")
            return
        
        dataframes = []
        
        for fichier in fichiers:
            chemin = os.path.join(self.dossier_csv, fichier)
            nom_categorie = fichier.replace('category_', '').replace('.csv', '')
            
            try:
                df = pd.read_csv(chemin, encoding='utf-8')
                df['categorie'] = nom_categorie
                dataframes.append(df)
                print(nom_categorie + ": " + str(len(df)) + " livres")
            except Exception as e:
                print("Erreur avec " + fichier + ": " + str(e))
        
        if dataframes:
            self.df_complet = pd.concat(dataframes, ignore_index=True)
            self.nettoyer_donnees()
            print("\nDATASET COMPLET: " + str(len(self.df_complet)) + " livres")
            print("Categories: " + str(self.df_complet['categorie'].nunique()))
        else:
            print("Aucune donnee chargee")
    
    def nettoyer_donnees(self):
        """Nettoie et prepare les donnees pour l'analyse"""
        print("\nNETTOYAGE DES DONNEES...")
        
        # Nettoyer les prix
        if 'prix' in self.df_complet.columns:
            self.df_complet['prix_numerique'] = self.df_complet['prix'].apply(
                lambda x: float(re.sub(r'[^\d.]', '', str(x))) if pd.notna(x) else 0.0
            )
        
        # Nettoyer les notes
        if 'note' in self.df_complet.columns:
            self.df_complet['note'] = pd.to_numeric(self.df_complet['note'], errors='coerce').fillna(0)
        
        # Nettoyer la disponibilite
        if 'disponibilite' in self.df_complet.columns:
            self.df_complet['disponibilite_clean'] = self.df_complet['disponibilite'].str.extract(r'(\d+)')[0]
            self.df_complet['disponibilite_clean'] = pd.to_numeric(
                self.df_complet['disponibilite_clean'], errors='coerce'
            ).fillna(0)
        
        print("Donnees nettoyees et pretes pour l'analyse")
    
    def statistiques_generales(self):
        """Affiche les statistiques generales du dataset"""
        if self.df_complet is None:
            print("Aucune donnee a analyser")
            return
        
        print("\n" + "="*60)
        print("STATISTIQUES GENERALES")
        print("="*60)
        
        # Informations de base
        print("Nombre total de livres: " + str(len(self.df_complet)))
        print("Nombre de categories: " + str(self.df_complet['categorie'].nunique()))
        
        # Statistiques par categorie
        print("\nREPARTITION PAR CATEGORIE:")
        stats_categories = self.df_complet['categorie'].value_counts()
        for categorie, count in stats_categories.items():
            pourcentage = (count / len(self.df_complet)) * 100
            print("   " + categorie.ljust(20) + " : " + str(count).rjust(3) + " livres (" + str(round(pourcentage, 1)) + "%)")
    
    def analyse_prix(self):
        """Analyse detaillee des prix"""
        if self.df_complet is None or 'prix_numerique' not in self.df_complet.columns:
            print("Donnees de prix non disponibles")
            return
        
        print("\n" + "="*60)
        print("ANALYSE DES PRIX")
        print("="*60)
        
        # Statistiques globales
        prix = self.df_complet['prix_numerique']
        print("Prix global:")
        print("   Moyenne: £" + str(round(prix.mean(), 2)))
        print("   Mediane: £" + str(round(prix.median(), 2)))
        print("   Minimum: £" + str(round(prix.min(), 2)))
        print("   Maximum: £" + str(round(prix.max(), 2)))
        
        # Prix par categorie
        print("\nPRIX MOYEN PAR CATEGORIE:")
        prix_par_categorie = self.df_complet.groupby('categorie')['prix_numerique'].agg([
            'count', 'mean', 'median'
        ]).round(2)
        
        prix_par_categorie_sorted = prix_par_categorie.sort_values('mean', ascending=False)
        
        for categorie, row in prix_par_categorie_sorted.iterrows():
            print("   " + categorie.ljust(20) + " : £" + str(row['mean']).rjust(6) + " (mediane: £" + str(row['median']) + ") - " + str(int(row['count'])) + " livres")
        
        # Top 5 livres les plus chers
        print("\nTOP 5 LIVRES LES PLUS CHERS:")
        livres_chers = self.df_complet.nlargest(5, 'prix_numerique')[['titre', 'prix_numerique', 'categorie']]
        for i, (_, livre) in enumerate(livres_chers.iterrows(), 1):
            titre_court = livre['titre'][:35] + "..." if len(livre['titre']) > 35 else livre['titre']
            print("   " + str(i) + ". £" + str(round(livre['prix_numerique'], 2)) + " - " + titre_court + " [" + livre['categorie'] + "]")
    
    def analyse_notes(self):
        """Analyse detaillee des notes"""
        if self.df_complet is None or 'note' not in self.df_complet.columns:
            print("Donnees de notes non disponibles")
            return
        
        print("\n" + "="*60)
        print("ANALYSE DES NOTES")
        print("="*60)
        
        # Distribution des notes
        print("DISTRIBUTION DES NOTES:")
        distribution_notes = self.df_complet['note'].value_counts().sort_index()
        
        for note, count in distribution_notes.items():
            etoiles = '*' * int(note) + '.' * (5 - int(note))
            pourcentage = (count / len(self.df_complet)) * 100
            print("   " + etoiles + " (" + str(note) + "/5) : " + str(count).rjust(3) + " livres (" + str(round(pourcentage, 1)) + "%)")
        
        # Note moyenne par categorie
        print("\nNOTE MOYENNE PAR CATEGORIE:")
        notes_par_categorie = self.df_complet.groupby('categorie')['note'].agg([
            'count', 'mean'
        ]).round(2)
        
        notes_par_categorie_sorted = notes_par_categorie.sort_values('mean', ascending=False)
        
        for categorie, row in notes_par_categorie_sorted.iterrows():
            print("   " + categorie.ljust(20) + " : " + str(row['mean']) + "/5 - " + str(int(row['count'])) + " livres")
    
    def analyse_disponibilite(self):
        """Analyse de la disponibilite des livres"""
        if self.df_complet is None or 'disponibilite_clean' not in self.df_complet.columns:
            print("Donnees de disponibilite non disponibles")
            return
        
        print("\n" + "="*60)
        print("ANALYSE DE LA DISPONIBILITE")
        print("="*60)
        
        # Statistiques de disponibilite
        dispo = self.df_complet['disponibilite_clean']
        print("Stock moyen par livre: " + str(round(dispo.mean(), 1)) + " unites")
        print("Stock median: " + str(round(dispo.median(), 1)) + " unites")
        
        # Categories avec le plus de stock
        print("\nCATEGORIES AVEC LE PLUS DE STOCK:")
        stock_par_categorie = self.df_complet.groupby('categorie')['disponibilite_clean'].mean().nlargest(5)
        for categorie, stock in stock_par_categorie.items():
            print("   " + categorie.ljust(20) + " : " + str(round(stock, 1)) + " unites en moyenne")
    
    def analyse_titres(self):
        """Analyse des mots les plus frequents dans les titres"""
        if self.df_complet is None or 'titre' not in self.df_complet.columns:
            return
        
        print("\n" + "="*60)
        print("ANALYSE DES TITRES")
        print("="*60)
        
        # Mots les plus frequents
        tous_les_titres = ' '.join(self.df_complet['titre'].astype(str)).lower()
        mots = re.findall(r'\b[a-z]{4,}\b', tous_les_titres)
        
        compteur_mots = Counter(mots)
        mots_frequents = compteur_mots.most_common(10)
        
        print("MOTS LES PLUS FREQUENTS DANS LES TITRES:")
        for mot, count in mots_frequents:
            print("   " + mot.ljust(15) + " : " + str(count).rjust(3) + " occurrences")
    
    def top_livres(self):
        """Affiche les meilleurs livres selon differents criteres"""
        if self.df_complet is None:
            return
        
        print("\n" + "="*60)
        print("TOP DES LIVRES")
        print("="*60)
        
        # Meilleur rapport qualite-prix (note/prix)
        if all(col in self.df_complet.columns for col in ['note', 'prix_numerique']):
            self.df_complet['rapport_qualite_prix'] = self.df_complet['note'] / self.df_complet['prix_numerique']
            
            print("\nMEILLEUR RAPPORT QUALITE-PRIX:")
            top_rapport = self.df_complet.nlargest(5, 'rapport_qualite_prix')[['titre', 'note', 'prix_numerique']]
            for i, (_, livre) in enumerate(top_rapport.iterrows(), 1):
                print("   " + str(i) + ". " + livre['titre'][:35] + "...")
                print("      Note: " + str(livre['note']) + "/5 - Prix: £" + str(round(livre['prix_numerique'], 2)))
        
        # Livres les mieux notes
        if 'note' in self.df_complet.columns:
            print("\nLIVRES LES MIEUX NOTES (5 etoiles):")
            livres_5_etoiles = self.df_complet[self.df_complet['note'] == 5][['titre', 'categorie', 'prix_numerique']]
            for i, (_, livre) in enumerate(livres_5_etoiles.head(5).iterrows(), 1):
                print("   " + str(i) + ". " + livre['titre'][:35] + "...")
                print("      Categorie: " + livre['categorie'] + " - Prix: £" + str(round(livre['prix_numerique'], 2)))
    
    def creer_visualisations_simple(self):
        """Cree des visualisations basiques sans seaborn"""
        try:
            import matplotlib.pyplot as plt
            
            print("\n" + "="*60)
            print("CREATION DE VISUALISATIONS SIMPLES")
            print("="*60)
            
            # Creer le dossier pour les graphiques
            os.makedirs('outputs/graphiques', exist_ok=True)
            
            # 1. Distribution des prix
            plt.figure(figsize=(10, 6))
            plt.hist(self.df_complet['prix_numerique'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Distribution des Prix des Livres')
            plt.xlabel('Prix (£)')
            plt.ylabel('Nombre de Livres')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('outputs/graphiques/distribution_prix.png', dpi=300, bbox_inches='tight')
            print("Graphique 1: outputs/graphiques/distribution_prix.png")
            plt.close()
            
            # 2. Notes par categorie (top 10 seulement)
            plt.figure(figsize=(12, 6))
            notes_par_cat = self.df_complet.groupby('categorie')['note'].mean().nlargest(10)
            notes_par_cat.plot(kind='bar', color='lightcoral')
            plt.title('Top 10 - Note Moyenne par Categorie')
            plt.xlabel('Categorie')
            plt.ylabel('Note Moyenne')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('outputs/graphiques/notes_par_categorie.png', dpi=300, bbox_inches='tight')
            print("Graphique 2: outputs/graphiques/notes_par_categorie.png")
            plt.close()
            
            # 3. Prix par categorie (top 10 seulement)
            plt.figure(figsize=(12, 6))
            prix_par_cat = self.df_complet.groupby('categorie')['prix_numerique'].mean().nlargest(10)
            prix_par_cat.plot(kind='bar', color='lightgreen')
            plt.title('Top 10 - Prix Moyen par Categorie')
            plt.xlabel('Categorie')
            plt.ylabel('Prix Moyen (£)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('outputs/graphiques/prix_par_categorie.png', dpi=300, bbox_inches='tight')
            print("Graphique 3: outputs/graphiques/prix_par_categorie.png")
            plt.close()
            
        except ImportError:
            print("Matplotlib non installe. Pas de graphiques crees.")
            print("Installez-le avec: pip install matplotlib")
    
    def rapport_complet(self):
        """Genere un rapport complet d'analyse"""
        print("DEMARRAGE DE L'ANALYSE COMPLETE")
        print("="*70)
        
        if self.df_complet is None:
            print("Aucune donnee a analyser")
            return
        
        self.statistiques_generales()
        self.analyse_prix()
        self.analyse_notes()
        self.analyse_disponibilite()
        self.analyse_titres()
        self.top_livres()
        self.creer_visualisations_simple()
        
        print("\n" + "="*70)
        print("ANALYSE TERMINEE AVEC SUCCES!")
        print("Les graphiques sont dans: outputs/graphiques/")

# Execution principale
if __name__ == "__main__":
    analyseur = AnalyseurLivres()
    analyseur.rapport_complet()