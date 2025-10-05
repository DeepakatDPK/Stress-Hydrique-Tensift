"""
Analyse statistique avancée multi-stations
Corrélations croisées, clustering et comparaisons
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.stats import pearsonr, spearmanr
import config
from pathlib import Path


class AdvancedAnalysis:
    """
    Analyses statistiques avancées pour comparer les stations.
    """
    
    def __init__(self, output_dir=None):
        if output_dir is None:
            self.output_dir = config.OUTPUT_DIR
        else:
            self.output_dir = Path(output_dir)
        
        self.stations_data = {}
        self.comparison_df = None
    
    def load_all_stations(self):
        """Charge les données de toutes les stations."""
        print("Chargement des données de toutes les stations...")
        
        for station_name in config.STATIONS_METADATA.keys():
            filepath = self.output_dir / f"{station_name}_with_anomalies.csv"
            
            if filepath.exists():
                df = pd.read_csv(filepath, parse_dates=['date'], index_col='date')
                self.stations_data[station_name] = df
                print(f"  - {station_name}: {len(df)} mois")
            else:
                print(f"  ⚠ {station_name}: fichier non trouvé")
        
        print(f"\nTotal: {len(self.stations_data)} stations chargées\n")
    
    def create_comparison_dataframe(self):
        """Crée un DataFrame comparatif avec les moyennes par station."""
        print("Création du DataFrame comparatif...")
        
        stats = []
        for station_name, df in self.stations_data.items():
            station_info = config.STATIONS_METADATA[station_name]
            
            stats.append({
                'station': station_name,
                'altitude': station_info['z'],
                'longitude': station_info['x'],
                'latitude': station_info['y'],
                'precip_mean': df['precipitation'].mean(),
                'precip_std': df['precipitation'].std(),
                'ndvi_mean': df['ndvi'].mean(),
                'ndvi_std': df['ndvi'].std(),
                'ndwi_mean': df['ndwi'].mean(),
                'lst_mean': df['lst'].mean(),
                'lst_std': df['lst'].std(),
                'stress_count': len(df[(df['ndvi_zscore'] < -1.5) | (df['lst_zscore'] > 1.5)])
            })
        
        self.comparison_df = pd.DataFrame(stats)
        print(f"DataFrame créé: {len(self.comparison_df)} stations\n")
        
        return self.comparison_df
    
    def compute_correlation_matrix(self):
        """Calcule la matrice de corrélation entre toutes les stations."""
        print("Calcul de la matrice de corrélation inter-stations...")
        
        # Créer une matrice avec les séries NDVI de chaque station
        ndvi_matrix = pd.DataFrame()
        
        for station_name, df in self.stations_data.items():
            ndvi_matrix[station_name] = df['ndvi'].values
        
        corr_matrix = ndvi_matrix.corr(method='pearson')
        
        # Visualiser
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn', 
                   center=0, vmin=-1, vmax=1, ax=ax, cbar_kws={'label': 'Corrélation'})
        ax.set_title('Matrice de Corrélation NDVI entre Stations', 
                    fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        filepath = config.PLOTS_DIR / "correlation_matrix_stations.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"  - Matrice sauvegardée: {filepath}\n")
        
        return corr_matrix
    
    def perform_clustering(self, n_clusters=3):
        """Clustering des stations basé sur leurs caractéristiques climatiques."""
        print(f"Clustering hiérarchique des stations (k={n_clusters})...")
        
        # Sélectionner les variables pour le clustering
        features = ['altitude', 'precip_mean', 'ndvi_mean', 'ndwi_mean', 'lst_mean']
        
        # Créer une copie pour gérer les NaN
        df_clean = self.comparison_df.copy()
        
        # Imputer les valeurs manquantes avec la médiane
        for col in features:
            if df_clean[col].isna().any():
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                print(f"  ⚠ Valeurs manquantes imputées pour {col} (médiane: {median_val:.2f})")
        
        X = df_clean[features].values
        
        # Normaliser
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_clean['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Ajouter les clusters au DataFrame original
        self.comparison_df['cluster'] = df_clean['cluster']
        
        # Clustering hiérarchique pour dendrogramme
        linkage_matrix = linkage(X_scaled, method='ward')
        
        # Visualiser le dendrogramme
        fig, ax = plt.subplots(figsize=(14, 6))
        dendrogram(linkage_matrix, labels=self.comparison_df['station'].values,
                  leaf_rotation=90, leaf_font_size=10, ax=ax)
        ax.set_title('Dendrogramme de Classification Hiérarchique des Stations',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Stations', fontsize=12)
        ax.set_ylabel('Distance (Ward)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        filepath = config.PLOTS_DIR / "clustering_dendrogram.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"  - Dendrogramme sauvegardé: {filepath}")
        
        # Afficher les clusters
        print("\nRésultats du clustering:")
        for cluster_id in range(n_clusters):
            stations = self.comparison_df[self.comparison_df['cluster'] == cluster_id]['station'].values
            print(f"  Cluster {cluster_id+1}: {', '.join(stations)}")
        print()
        
        return self.comparison_df
    
    def plot_bivariate_analysis(self):
        """Analyse bivariée: altitude vs NDVI, précipitations vs NDVI, etc."""
        print("Génération des graphiques d'analyse bivariée...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 1. Altitude vs NDVI
        ax = axes[0, 0]
        scatter = ax.scatter(self.comparison_df['altitude'], self.comparison_df['ndvi_mean'],
                           c=self.comparison_df['cluster'], cmap='viridis', s=100, 
                           edgecolors='black', linewidth=1.5, alpha=0.7)
        for idx, row in self.comparison_df.iterrows():
            ax.annotate(row['station'], (row['altitude'], row['ndvi_mean']),
                       fontsize=8, ha='right', va='bottom')
        ax.set_xlabel('Altitude (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('NDVI Moyen', fontsize=11, fontweight='bold')
        ax.set_title('Altitude vs Santé Végétale', fontsize=12, pad=10)
        ax.grid(True, alpha=0.3)
        
        # 2. Précipitations vs NDVI
        ax = axes[0, 1]
        scatter = ax.scatter(self.comparison_df['precip_mean'], self.comparison_df['ndvi_mean'],
                           c=self.comparison_df['cluster'], cmap='viridis', s=100,
                           edgecolors='black', linewidth=1.5, alpha=0.7)
        for idx, row in self.comparison_df.iterrows():
            ax.annotate(row['station'], (row['precip_mean'], row['ndvi_mean']),
                       fontsize=8, ha='right', va='bottom')
        ax.set_xlabel('Précipitations Moyennes (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('NDVI Moyen', fontsize=11, fontweight='bold')
        ax.set_title('Précipitations vs Santé Végétale', fontsize=12, pad=10)
        ax.grid(True, alpha=0.3)
        
        # 3. Température vs NDVI
        ax = axes[1, 0]
        scatter = ax.scatter(self.comparison_df['lst_mean'], self.comparison_df['ndvi_mean'],
                           c=self.comparison_df['cluster'], cmap='viridis', s=100,
                           edgecolors='black', linewidth=1.5, alpha=0.7)
        for idx, row in self.comparison_df.iterrows():
            ax.annotate(row['station'], (row['lst_mean'], row['ndvi_mean']),
                       fontsize=8, ha='right', va='bottom')
        ax.set_xlabel('Température Moyenne (°C)', fontsize=11, fontweight='bold')
        ax.set_ylabel('NDVI Moyen', fontsize=11, fontweight='bold')
        ax.set_title('Température vs Santé Végétale', fontsize=12, pad=10)
        ax.grid(True, alpha=0.3)
        
        # 4. Stress Count vs Précipitations
        ax = axes[1, 1]
        scatter = ax.scatter(self.comparison_df['precip_mean'], self.comparison_df['stress_count'],
                           c=self.comparison_df['cluster'], cmap='viridis', s=100,
                           edgecolors='black', linewidth=1.5, alpha=0.7)
        for idx, row in self.comparison_df.iterrows():
            ax.annotate(row['station'], (row['precip_mean'], row['stress_count']),
                       fontsize=8, ha='right', va='bottom')
        ax.set_xlabel('Précipitations Moyennes (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Nombre de Périodes de Stress', fontsize=11, fontweight='bold')
        ax.set_title('Précipitations vs Fréquence du Stress', fontsize=12, pad=10)
        ax.grid(True, alpha=0.3)
        
        # Colorbar commune
        cbar = plt.colorbar(scatter, ax=axes, orientation='horizontal', 
                           pad=0.08, aspect=40, shrink=0.8)
        cbar.set_label('Cluster', fontsize=11, fontweight='bold')
        
        plt.suptitle('Analyses Bivariées Multi-Stations', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        filepath = config.PLOTS_DIR / "bivariate_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"  - Analyse bivariée sauvegardée: {filepath}\n")
    
    def export_summary_table(self):
        """Exporte un tableau récapitulatif en CSV."""
        filepath = self.output_dir / "stations_comparison_summary.csv"
        self.comparison_df.to_csv(filepath, index=False)
        print(f"Tableau récapitulatif exporté: {filepath}\n")


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ANALYSE STATISTIQUE AVANCÉE MULTI-STATIONS")
    print("=" * 80)
    print()
    
    # Initialiser
    analysis = AdvancedAnalysis()
    
    # Charger toutes les stations
    analysis.load_all_stations()
    
    # Créer le DataFrame comparatif
    df_comparison = analysis.create_comparison_dataframe()
    
    print("=" * 80)
    print("STATISTIQUES DESCRIPTIVES")
    print("=" * 80)
    print()
    print(df_comparison[['station', 'altitude', 'precip_mean', 'ndvi_mean', 
                         'lst_mean', 'stress_count']].to_string(index=False))
    print()
    
    # Matrice de corrélation
    print("=" * 80)
    print("ANALYSE DE CORRÉLATION")
    print("=" * 80)
    print()
    corr_matrix = analysis.compute_correlation_matrix()
    
    # Clustering
    print("=" * 80)
    print("CLUSTERING DES STATIONS")
    print("=" * 80)
    print()
    df_clustered = analysis.perform_clustering(n_clusters=3)
    
    # Analyses bivariées
    print("=" * 80)
    print("ANALYSES BIVARIÉES")
    print("=" * 80)
    print()
    analysis.plot_bivariate_analysis()
    
    # Exporter
    analysis.export_summary_table()
    
    print("=" * 80)
    print("ANALYSE TERMINÉE")
    print("=" * 80)
    print()
    print("Fichiers générés:")
    print(f"  - {config.PLOTS_DIR}/correlation_matrix_stations.png")
    print(f"  - {config.PLOTS_DIR}/clustering_dendrogram.png")
    print(f"  - {config.PLOTS_DIR}/bivariate_analysis.png")
    print(f"  - {config.OUTPUT_DIR}/stations_comparison_summary.csv")