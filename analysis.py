"""
Module d'analyse statistique du stress hydrique
Calcule les anomalies (Z-scores) pour détecter les périodes de stress
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config
from precipitation import PrecipitationManager
from gee_data import SatelliteDataManager


class StressAnalysis:
    """
    Analyse du stress hydrique pour une station donnée.
    Combine les données de précipitations et les indices satellitaires
    pour détecter les anomalies.
    """
    
    def __init__(self, station_name):
        """
        Initialise l'analyse pour une station.
        
        Args:
            station_name (str): Nom de la station à analyser
        """
        if station_name not in config.STATIONS_METADATA:
            raise ValueError(f"Station '{station_name}' non trouvée dans config.py")
        
        self.station_name = station_name
        self.station_info = config.STATIONS_METADATA[station_name]
        self.results_df = None
        
        print(f"Analyse initialisée pour la station : {station_name}")
    
    def run_historical_analysis(self, precip_manager, satellite_manager, 
                                start_year=None, end_year=None):
        """
        Effectue l'analyse historique complète pour la station.
        Boucle sur chaque mois de la période et extrait toutes les données.
        
        Args:
            precip_manager (PrecipitationManager): Gestionnaire de précipitations
            satellite_manager (SatelliteDataManager): Gestionnaire de données satellites
            start_year (int, optional): Année de début (défaut: depuis config)
            end_year (int, optional): Année de fin (défaut: depuis config)
        
        Returns:
            pd.DataFrame: DataFrame avec toutes les données extraites
        """
        print("=" * 70)
        print(f"ANALYSE HISTORIQUE - {self.station_name}")
        print("=" * 70)
        print()
        
        # Définir la période d'analyse
        if start_year is None or end_year is None:
            start_date = pd.to_datetime(config.ANALYSIS_PERIOD[0])
            end_date = pd.to_datetime(config.ANALYSIS_PERIOD[1])
            start_year = start_date.year
            end_year = end_date.year
        
        print(f"Période d'analyse : {start_year} à {end_year}")
        print()
        
        # Obtenir les données de précipitations mensuelles
        print("Extraction des données de précipitations...")
        monthly_precip = precip_manager.get_station_monthly_data(self.station_name)
        
        # Filtrer sur la période d'analyse
        monthly_precip = monthly_precip[
            (monthly_precip.index.year >= start_year) & 
            (monthly_precip.index.year <= end_year)
        ]
        print(f"✓ {len(monthly_precip)} mois de données de précipitations extraits")
        print()
        
        # Préparer le DataFrame de résultats
        data_records = []
        
        print("Extraction des indices satellitaires...")
        print("(Cela peut prendre plusieurs minutes selon la période)")
        print()
        
        total_months = len(monthly_precip)
        processed = 0
        
        for date, precip_value in monthly_precip.items():
            year = date.year
            month = date.month
            
            # Afficher la progression tous les 12 mois
            if processed % 12 == 0:
                print(f"Progression : {processed}/{total_months} mois traités "
                      f"({processed/total_months*100:.1f}%)")
            
            # Extraire les indices satellitaires
            try:
                indices = satellite_manager.get_monthly_indices(
                    year, month, self.station_info
                )
            except Exception as e:
                print(f"  ⚠ Erreur pour {year}-{month:02d}: {e}")
                indices = {'ndvi': None, 'ndwi': None, 'lst': None}
            
            # Créer l'enregistrement
            record = {
                'date': date,
                'year': year,
                'month': month,
                'precipitation': precip_value,
                'ndvi': indices['ndvi'],
                'ndwi': indices['ndwi'],
                'lst': indices['lst']
            }
            
            data_records.append(record)
            processed += 1
        
        print(f"✓ Traitement terminé : {processed} mois analysés")
        print()
        
        # Créer le DataFrame
        self.results_df = pd.DataFrame(data_records)
        self.results_df.set_index('date', inplace=True)
        
        # Sauvegarder les résultats bruts
        output_file = config.OUTPUT_DIR / f"{self.station_name}_raw_data.csv"
        self.results_df.to_csv(output_file)
        print(f"✓ Données brutes sauvegardées : {output_file}")
        print()
        
        return self.results_df
    
    def calculate_anomalies(self):
        """
        Calcule les anomalies (Z-scores) pour chaque indice.
        Le Z-score mesure à quel point une valeur s'écarte de la moyenne historique
        pour le même mois de l'année.
        
        Returns:
            pd.DataFrame: DataFrame avec les colonnes de Z-score ajoutées
        """
        if self.results_df is None:
            raise RuntimeError("Exécutez d'abord run_historical_analysis()")
        
        print("=" * 70)
        print("CALCUL DES ANOMALIES (Z-SCORES)")
        print("=" * 70)
        print()
        
        df = self.results_df.copy()
        
        # Liste des indices à analyser
        indices = ['precipitation', 'ndvi', 'ndwi', 'lst']
        
        for index_name in indices:
            print(f"Calcul du Z-score pour : {index_name}")
            
            # Calculer la moyenne et l'écart-type pour chaque mois (1-12)
            # en utilisant toutes les années disponibles
            monthly_stats = df.groupby('month')[index_name].agg(['mean', 'std'])
            
            # Ajouter un petit epsilon pour éviter la division par zéro
            monthly_stats['std'] = monthly_stats['std'].replace(0, config.EPSILON)
            monthly_stats['std'] = monthly_stats['std'].fillna(config.EPSILON)
            
            # Calculer le Z-score pour chaque ligne
            zscore_col = f"{index_name}_zscore"
            df[zscore_col] = df.apply(
                lambda row: (row[index_name] - monthly_stats.loc[row['month'], 'mean']) / 
                           monthly_stats.loc[row['month'], 'std']
                if pd.notna(row[index_name]) else np.nan,
                axis=1
            )
            
            # Statistiques du Z-score
            valid_zscores = df[zscore_col].dropna()
            if len(valid_zscores) > 0:
                print(f"  - Moyenne du Z-score : {valid_zscores.mean():.4f}")
                print(f"  - Écart-type du Z-score : {valid_zscores.std():.4f}")
                print(f"  - Min/Max : {valid_zscores.min():.2f} / {valid_zscores.max():.2f}")
            else:
                print(f"  ⚠ Aucune valeur valide pour {index_name}")
            print()
        
        self.results_df = df
        
        # Sauvegarder les résultats avec anomalies
        output_file = config.OUTPUT_DIR / f"{self.station_name}_with_anomalies.csv"
        self.results_df.to_csv(output_file)
        print(f"✓ Données avec anomalies sauvegardées : {output_file}")
        print()
        
        return self.results_df
    
    def get_stress_periods(self, threshold=-1.5):
        """
        Identifie les périodes de stress hydrique potentiel.
        Un stress est détecté quand NDVI est significativement bas
        (Z-score < threshold) et/ou LST est significativement haut
        (Z-score > -threshold).
        
        Args:
            threshold (float): Seuil du Z-score pour détecter une anomalie
        
        Returns:
            pd.DataFrame: Sous-ensemble du DataFrame avec les périodes de stress
        """
        if self.results_df is None or 'ndvi_zscore' not in self.results_df.columns:
            raise RuntimeError("Exécutez d'abord calculate_anomalies()")
        
        # Détecter les périodes de stress
        stress_mask = (
            (self.results_df['ndvi_zscore'] < threshold) |
            (self.results_df['lst_zscore'] > -threshold)
        )
        
        stress_periods = self.results_df[stress_mask].copy()
        
        return stress_periods


# ============================================================================
# BLOC DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU MODULE ANALYSIS")
    print("=" * 70)
    print()
    
    # Station de test
    station_test = "MARRAKECH"
    
    # Initialiser les gestionnaires
    print("Initialisation des gestionnaires...")
    precip_manager = PrecipitationManager(config.RAIN_DATA_PATH)
    sat_manager = SatelliteDataManager(project_id='votre-project-id')
    print()
    
    # Créer l'analyse
    analysis = StressAnalysis(station_test)
    print()
    
    # IMPORTANT : Pour le test, on limite à une période courte
    # Pour l'analyse complète, utilisez les dates de config.ANALYSIS_PERIOD
    print("⚠ TEST LIMITÉ : Analyse uniquement 2018-2019 (2 ans)")
    print("   Pour l'analyse complète, modifiez start_year et end_year")
    print()
    
    # Exécuter l'analyse historique (limité pour le test)
    df_results = analysis.run_historical_analysis(
        precip_manager, 
        sat_manager,
        start_year=2018,
        end_year=2019
    )
    
    print("Aperçu des données brutes :")
    print(df_results.head())
    print()
    
    # Calculer les anomalies
    df_with_anomalies = analysis.calculate_anomalies()
    
    print("=" * 70)
    print("APERÇU DES RÉSULTATS AVEC ANOMALIES")
    print("=" * 70)
    print()
    print(df_with_anomalies[['precipitation', 'ndvi', 'lst', 
                             'precipitation_zscore', 'ndvi_zscore', 
                             'lst_zscore']].head(10))
    print()
    
    # Identifier les périodes de stress
    stress_periods = analysis.get_stress_periods(threshold=-1.5)
    
    print("=" * 70)
    print(f"PÉRIODES DE STRESS DÉTECTÉES ({len(stress_periods)} mois)")
    print("=" * 70)
    print()
    if len(stress_periods) > 0:
        print(stress_periods[['precipitation', 'ndvi', 'lst', 
                              'ndvi_zscore', 'lst_zscore']].head(10))
    else:
        print("Aucune période de stress détectée avec le seuil actuel")
    print()
    
    print("=" * 70)
    print("✓ TESTS RÉUSSIS")
    print("=" * 70)
    print()
    print("Le module analysis.py est prêt à être utilisé !")
    print()
    print("PROCHAINE ÉTAPE :")
    print("- Vérifiez les fichiers CSV générés dans le dossier output/")
    print("- Passez à l'étape suivante : visualization.py")