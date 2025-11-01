# analyser_donnees.py - Version simplifiee sans emojis
import pandas as pd
import os
import re

def nettoyer_prix(prix_str):
    """Nettoie le prix qui contient des caracteres d'encodage"""
    if pd.isna(prix_str):
        return 0.0
    
    # Plusieurs methodes pour nettoyer le prix
    prix_str = str(prix_str)
    
    # Methode 1: Supprimer tous les caracteres non numeriques sauf le point
    prix_nettoye = re.sub(r'[^\d.]', '', prix_str)
    
    # Methode 2: Si ca ne marche pas, chercher le pattern numerique
    if not prix_nettoye:
        match = re.search(r'(\d+\.\d+)', prix_str)
        if match:
            prix_nettoye = match.group(1)
        else:
            return 0.0
    
    try:
        return float(prix_nettoye)
    except:
        return 0.0

def analyser_categorie(fichier_csv):
    """Analyse les donnees d'une categorie"""
    
    try:
        # Lire le fichier CSV avec encodage UTF-8
        df = pd.read_csv(fichier_csv, encoding='utf-8')
        
        nom_categorie = os.path.basename(fichier_csv).replace('category_', '').replace('.csv', '')
        
        print("\nANALYSE DE LA CATEGORIE : " + nom_categorie.upper())
        print("=" * 50)
        
        # Informations de base
        print("Nombre total de livres : " + str(len(df)))
        print("Colonnes disponibles : " + str(list(df.columns)))
        
        # Apercu des donnees
        print("\nAPERÇU DES DONNEES :")
        print(df[['titre', 'prix', 'note']].head(3))
        
        # Nettoyer les prix
        if 'prix' in df.columns:
            print("\nEXEMPLE DE PRIX AVANT NETTOYAGE :")
            print("   " + str(df['prix'].iloc[0]))
            
            # Appliquer le nettoyage
            df['prix_numerique'] = df['prix'].apply(nettoyer_prix)
            
            # Statistiques sur les prix
            print("\nSTATISTIQUES DES PRIX :")
            print("   Prix moyen : £" + str(round(df['prix_numerique'].mean(), 2)))
            print("   Prix minimum : £" + str(round(df['prix_numerique'].min(), 2)))
            print("   Prix maximum : £" + str(round(df['prix_numerique'].max(), 2)))
            print("   Prix median : £" + str(round(df['prix_numerique'].median(), 2)))
            
            # Top 5 des livres les plus chers
            print("\nTOP 5 DES LIVRES LES PLUS CHERS :")
            livres_chers = df.nlargest(5, 'prix_numerique')[['titre', 'prix_numerique']]
            for i, (index, ligne) in enumerate(livres_chers.iterrows(), 1):
                titre_court = ligne['titre'][:30] + "..." if len(ligne['titre']) > 30 else ligne['titre']
                print("   " + str(i) + ". £" + str(round(ligne['prix_numerique'], 2)) + " - " + titre_court)
        
        # Analyse des notes
        if 'note' in df.columns:
            print("\nDISTRIBUTION DES NOTES :")
            if df['note'].dtype == 'object':
                # Si les notes sont encore des strings, les convertir
                df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0)
            
            comptage_notes = df['note'].value_counts().sort_index()
            for note, compte in comptage_notes.items():
                etoiles = '*' * int(note) + '.' * (5 - int(note))
                print("   " + etoiles + " (" + str(int(note)) + "/5) : " + str(compte) + " livre(s)")
            
            print("   Note moyenne : " + str(round(df['note'].mean(), 1)) + "/5")
        
        # Analyse de la disponibilite
        if 'disponibilite' in df.columns:
            print("\nDISPONIBILITE :")
            disponibilite_counts = df['disponibilite'].value_counts()
            for dispo, compte in disponibilite_counts.items():
                # Nettoyer le texte de disponibilite
                dispo_nettoye = dispo.replace('\n', ' ').strip()
                print("   " + dispo_nettoye + " : " + str(compte) + " livre(s)")
        
        return df
        
    except Exception as e:
        print("ERREUR avec " + fichier_csv + " : " + str(e))
        import traceback
        traceback.print_exc()
        return None

def analyser_toutes_categories():
    """Analyse tous les fichiers CSV generes"""
    
    dossier_csv = "outputs/csv"
    
    if os.path.exists(dossier_csv):
        fichiers = [f for f in os.listdir(dossier_csv) if f.endswith('.csv')]
        
        if fichiers:
            print("DEBUT DE L'ANALYSE DES DONNEES")
            print("=" * 60)
            print("Fichiers trouves : " + str(fichiers))
            
            for fichier in fichiers:
                chemin_complet = os.path.join(dossier_csv, fichier)
                print("\n" + "="*40)
                analyser_categorie(chemin_complet)
                
        else:
            print("Aucun fichier CSV trouve dans outputs/csv/")
    else:
        print("Le dossier 'outputs/csv' n'existe pas.")

# Fonction pour examiner les donnees brutes
def examiner_donnees_brutes():
    """Examine les donnees brutes pour comprendre le format"""
    dossier_csv = "outputs/csv"
    
    if not os.path.exists(dossier_csv):
        print("Dossier outputs/csv/ non trouve")
        return
    
    fichiers = [f for f in os.listdir(dossier_csv) if f.endswith('.csv')]
    
    for fichier in fichiers:
        chemin = os.path.join(dossier_csv, fichier)
        print("\nEXAMEN DES DONNEES BRUTES : " + fichier)
        print("=" * 40)
        
        try:
            # Lire sans nettoyage
            df = pd.read_csv(chemin, encoding='utf-8')
            
            # Afficher les premieres lignes
            print("Premieres lignes du CSV :")
            for i in range(min(2, len(df))):
                print("Ligne " + str(i) + ":")
                for col in df.columns:
                    print("  " + col + ": " + repr(df[col].iloc[i]))
            
            # Analyser les prix
            if 'prix' in df.columns:
                print("\nAnalyse des prix :")
                prix_exemple = df['prix'].iloc[0]
                print("Premier prix brut: " + repr(prix_exemple))
                print("Type: " + str(type(prix_exemple)))
                print("Caracteres: " + str([ord(c) for c in str(prix_exemple)]))
                
        except Exception as e:
            print("Erreur: " + str(e))

if __name__ == "__main__":
    # Choisissez une option :
    
    # Option 1: Analyse normale
    analyser_toutes_categories()
    
    # Option 2: Examiner les donnees brutes (pour debug)
    # examiner_donnees_brutes()