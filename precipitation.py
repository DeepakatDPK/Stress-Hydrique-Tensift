"""
Module de gestion des données pluviométriques
Charge, nettoie et agrège les données de précipitations journalières
"""

import pandas as pd
import numpy as np
import config


class PrecipitationManager:
    """
    Gestionnaire des données de précipitations pour le bassin du Tensift.
    Charge les données depuis un fichier Excel et fournit des méthodes
    pour extraire et traiter les séries temporelles par station.
    """
    
    def __init__(self, filepath):
        """
        Initialise le gestionnaire et charge les données brutes.
        
        Args:
            filepath (Path ou str): Chemin vers le fichier Excel des précipitations
        """
        print(f"Chargement des données de précipitations depuis : {filepath}")
        
        # Charger le fichier Excel
        # La première colonne est la date, les autres sont les stations
        self.raw_df = pd.read_excel(filepath)
        
        # Renommer la première colonne en 'DATE' si nécessaire
        if self.raw_df.columns[0] != 'DATE':
            self.raw_df.rename(columns={self.raw_df.columns[0]: 'DATE'}, inplace=True)
        
        # Convertir la colonne DATE en datetime
        self.raw_df['DATE'] = pd.to_datetime(self.raw_df['DATE'])
        
        # Définir DATE comme index
        self.raw_df.set_index('DATE', inplace=True)
        
        print(f"✓ Données chargées : {len(self.raw_df)} jours")
        print(f"✓ Période couverte : {self.raw_df.index.min()} à {self.raw_df.index.max()}")
        print(f"✓ Stations disponibles : {list(self.raw_df.columns)}")
        print()
    
    def get_station_timeseries(self, station_name):
        """
        Extrait et nettoie les données journalières pour une station donnée.
        
        Opérations effectuées :
        - Sélection de la colonne de la station
        - Conversion des valeurs non numériques en NaN
        - Suppression des valeurs négatives (erreurs de mesure)
        - Interpolation linéaire pour combler les petits trous
        
        Args:
            station_name (str): Nom de la station (doit correspondre aux colonnes)
        
        Returns:
            pd.Series: Série temporelle journalière nettoyée avec index datetime
        """
        if station_name not in self.raw_df.columns:
            raise ValueError(f"Station '{station_name}' non trouvée. "
                           f"Stations disponibles : {list(self.raw_df.columns)}")
        
        print(f"Extraction des données pour la station : {station_name}")
        
        # Extraire la colonne de la station
        series = self.raw_df[station_name].copy()
        
        # Compter les valeurs initiales
        total_values = len(series)
        initial_na = series.isna().sum()
        
        # Convertir les valeurs non numériques en NaN
        # (comme 'M', 'NAN', ou toute chaîne de caractères)
        series = pd.to_numeric(series, errors='coerce')
        
        # Supprimer les valeurs négatives (erreurs de mesure)
        series[series < 0] = np.nan
        
        # Compter les NaN après nettoyage
        na_after_cleaning = series.isna().sum()
        
        # Interpolation linéaire pour combler les trous
        # Limite : ne pas interpoler au-delà de 7 jours consécutifs
        series = series.interpolate(method='linear', limit=7)
        
        # Compter les NaN après interpolation
        final_na = series.isna().sum()
        
        print(f"  - Valeurs totales : {total_values}")
        print(f"  - Valeurs manquantes initiales : {initial_na} ({initial_na/total_values*100:.1f}%)")
        print(f"  - Valeurs manquantes après nettoyage : {na_after_cleaning}")
        print(f"  - Valeurs manquantes après interpolation : {final_na}")
        print(f"  ✓ Série nettoyée pour {station_name}")
        print()
        
        return series
    
    def get_monthly_rainfall(self, daily_series):
        """
        Agrège une série journalière en cumuls mensuels.
        
        Args:
            daily_series (pd.Series): Série temporelle journalière
        
        Returns:
            pd.Series: Série temporelle mensuelle avec les cumuls de précipitations
        """
        # Agréger par mois (somme des précipitations)
        # 'M' pour Month end (fin de mois)
        monthly_series = daily_series.resample('M').sum()
        
        # Remplacer les mois avec trop de valeurs manquantes par NaN
        # On compte les jours valides par mois
        daily_count = daily_series.resample('M').count()
        
        # Si un mois a moins de 20 jours de données, on le marque comme invalide
        monthly_series[daily_count < 20] = np.nan
        
        return monthly_series
    
    def get_station_monthly_data(self, station_name):
        """
        Méthode pratique qui combine get_station_timeseries et get_monthly_rainfall.
        
        Args:
            station_name (str): Nom de la station
        
        Returns:
            pd.Series: Série mensuelle des cumuls de précipitations
        """
        daily = self.get_station_timeseries(station_name)
        monthly = self.get_monthly_rainfall(daily)
        return monthly


# ============================================================================
# BLOC DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU MODULE PRECIPITATION")
    print("=" * 70)
    print()
    
    # Créer une instance du gestionnaire
    precip_manager = PrecipitationManager(config.RAIN_DATA_PATH)
    
    # Test avec la station MARRAKECH
    station_test = "MARRAKECH"
    
    print("=" * 70)
    print(f"TEST 1 : Extraction des données journalières pour {station_test}")
    print("=" * 70)
    print()
    
    daily_data = precip_manager.get_station_timeseries(station_test)
    
    print(f"Données journalières - Premières lignes :")
    print(daily_data.head(10))
    print()
    print(f"Statistiques descriptives :")
    print(daily_data.describe())
    print()
    
    print("=" * 70)
    print(f"TEST 2 : Agrégation en cumuls mensuels pour {station_test}")
    print("=" * 70)
    print()
    
    monthly_data = precip_manager.get_monthly_rainfall(daily_data)
    
    print(f"Données mensuelles - Premières lignes :")
    print(monthly_data.head(12))
    print()
    print(f"Statistiques descriptives :")
    print(monthly_data.describe())
    print()
    
    print("=" * 70)
    print(f"TEST 3 : Méthode combinée pour {station_test}")
    print("=" * 70)
    print()
    
    monthly_combined = precip_manager.get_station_monthly_data(station_test)
    
    print(f"Données mensuelles combinées - 5 premières lignes :")
    print(monthly_combined.head())
    print()
    
    print("=" * 70)
    print("✓ TOUS LES TESTS RÉUSSIS")
    print("=" * 70)
    print()
    print("Le module precipitation.py est prêt à être utilisé !")