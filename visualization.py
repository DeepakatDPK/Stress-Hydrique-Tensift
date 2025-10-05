"""
Module de visualisation des résultats
Génère des graphiques et des cartes pour l'analyse du stress hydrique
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import config
from pathlib import Path


class ReportGenerator:
    """
    Générateur de rapports visuels pour l'analyse du stress hydrique.
    Crée des graphiques de séries temporelles et des cartes d'anomalies.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialise le générateur de rapports.
        
        Args:
            output_dir (Path ou str, optional): Dossier de sortie pour les visualisations
        """
        if output_dir is None:
            self.output_dir = config.OUTPUT_DIR
        else:
            self.output_dir = Path(output_dir)
        
        # S'assurer que les dossiers existent
        config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        config.MAPS_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"Générateur de rapports initialisé")
        print(f"Dossier graphiques : {config.PLOTS_DIR}")
        print(f"Dossier cartes : {config.MAPS_DIR}")
        print()
    
    def generate_timeseries_plot(self, df_analysis, station_name, save=True):
        """
        Crée un graphique de séries temporelles comparant les anomalies
        de stress (NDVI, LST) avec les précipitations.
        
        Args:
            df_analysis (pd.DataFrame): DataFrame avec les colonnes de Z-score
            station_name (str): Nom de la station
            save (bool): Si True, sauvegarde le graphique
        
        Returns:
            matplotlib.figure.Figure: La figure créée
        """
        print(f"Génération du graphique pour {station_name}...")
        
        # Créer une figure avec 2 sous-graphiques
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Titre principal
        fig.suptitle(f'Analyse du Stress Hydrique - Station {station_name}', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        # ================================================================
        # GRAPHIQUE 1 : Indices de stress (Z-scores)
        # ================================================================
        
        # NDVI Z-score (végétation)
        ax1.plot(df_analysis.index, df_analysis['ndvi_zscore'], 
                label='NDVI Z-score (Santé végétation)', 
                color='green', linewidth=1.5, marker='o', markersize=3)
        
        # LST Z-score (température)
        ax1.plot(df_analysis.index, df_analysis['lst_zscore'], 
                label='LST Z-score (Température)', 
                color='red', linewidth=1.5, marker='s', markersize=3)
        
        # NDWI Z-score (humidité)
        ax1.plot(df_analysis.index, df_analysis['ndwi_zscore'], 
                label='NDWI Z-score (Humidité)', 
                color='blue', linewidth=1.5, marker='^', markersize=3, alpha=0.7)
        
        # Ligne de référence à 0 (moyenne historique)
        ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        
        # Zones de stress
        ax1.axhspan(-3, -1.5, alpha=0.1, color='red', label='Zone de stress modéré')
        ax1.axhspan(-3, -1.5, alpha=0.2, color='red')
        
        # Configuration du graphique 1
        ax1.set_ylabel('Z-score (écarts à la normale)', fontsize=11, fontweight='bold')
        ax1.set_title('Anomalies des Indices Satellitaires', fontsize=12, pad=10)
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3, linestyle=':')
        ax1.set_ylim(-3, 3)
        
        # ================================================================
        # GRAPHIQUE 2 : Précipitations
        # ================================================================
        
        # Précipitations mensuelles (barres)
        ax2.bar(df_analysis.index, df_analysis['precipitation'], 
               width=25, color='steelblue', alpha=0.7, 
               label='Précipitations mensuelles (mm)')
        
        # Z-score des précipitations (ligne)
        ax2_twin = ax2.twinx()
        ax2_twin.plot(df_analysis.index, df_analysis['precipitation_zscore'], 
                     color='navy', linewidth=2, marker='o', markersize=4,
                     label='Précipitations Z-score')
        ax2_twin.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax2_twin.set_ylabel('Z-score précipitations', fontsize=10)
        ax2_twin.set_ylim(-3, 3)
        ax2_twin.legend(loc='upper right', fontsize=9)
        
        # Configuration du graphique 2
        ax2.set_ylabel('Précipitations (mm)', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax2.set_title('Précipitations Mensuelles', fontsize=12, pad=10)
        ax2.legend(loc='upper left', fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle=':')
        
        # Format de l'axe des dates
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Ajustement de la mise en page
        plt.tight_layout()
        
        # Sauvegarder
        if save:
            filename = config.PLOTS_DIR / f"{station_name}_timeseries.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvegardé : {filename}")
        
        return fig
    
    def generate_correlation_plot(self, df_analysis, station_name, save=True):
        """
        Crée un graphique de corrélation entre précipitations et indices.
        
        Args:
            df_analysis (pd.DataFrame): DataFrame avec les données
            station_name (str): Nom de la station
            save (bool): Si True, sauvegarde le graphique
        
        Returns:
            matplotlib.figure.Figure: La figure créée
        """
        print(f"Génération du graphique de corrélation pour {station_name}...")
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f'Corrélation Précipitations vs Indices - {station_name}', 
                     fontsize=14, fontweight='bold')
        
        # Filtrer les données valides
        df_valid = df_analysis.dropna(subset=['precipitation', 'ndvi', 'ndwi', 'lst'])
        
        indices = [
            ('ndvi', 'NDVI (Santé végétation)', 'green'),
            ('ndwi', 'NDWI (Humidité)', 'blue'),
            ('lst', 'LST (Température)', 'red')
        ]
        
        for i, (index_name, title, color) in enumerate(indices):
            ax = axes[i]
            
            # Scatter plot
            ax.scatter(df_valid['precipitation'], df_valid[index_name], 
                      alpha=0.6, s=50, color=color, edgecolors='black', linewidth=0.5)
            
            # Ligne de tendance
            if len(df_valid) > 2:
                z = np.polyfit(df_valid['precipitation'], df_valid[index_name], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(df_valid['precipitation'].min(), 
                                     df_valid['precipitation'].max(), 100)
                ax.plot(x_trend, p(x_trend), "r--", linewidth=2, alpha=0.8)
                
                # Calculer la corrélation
                corr = df_valid['precipitation'].corr(df_valid[index_name])
                ax.text(0.05, 0.95, f'Corrélation: {corr:.3f}', 
                       transform=ax.transAxes, fontsize=10, 
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel('Précipitations (mm)', fontsize=10)
            ax.set_ylabel(title, fontsize=10)
            ax.set_title(title, fontsize=11, pad=10)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = config.PLOTS_DIR / f"{station_name}_correlation.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvegardé : {filename}")
        
        return fig
    
    def generate_monthly_climatology(self, df_analysis, station_name, save=True):
        """
        Crée un graphique de climatologie mensuelle (moyennes par mois).
        
        Args:
            df_analysis (pd.DataFrame): DataFrame avec les données
            station_name (str): Nom de la station
            save (bool): Si True, sauvegarde le graphique
        
        Returns:
            matplotlib.figure.Figure: La figure créée
        """
        print(f"Génération de la climatologie mensuelle pour {station_name}...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Climatologie Mensuelle - {station_name}', 
                     fontsize=14, fontweight='bold')
        
        # Calculer les moyennes mensuelles
        monthly_avg = df_analysis.groupby('month').agg({
            'precipitation': 'mean',
            'ndvi': 'mean',
            'ndwi': 'mean',
            'lst': 'mean'
        })
        
        # Calculer les écarts-types
        monthly_std = df_analysis.groupby('month').agg({
            'precipitation': 'std',
            'ndvi': 'std',
            'ndwi': 'std',
            'lst': 'std'
        })
        
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        # Précipitations
        ax = axes[0, 0]
        ax.bar(range(1, 13), monthly_avg['precipitation'], 
              yerr=monthly_std['precipitation'], capsize=5, 
              color='steelblue', alpha=0.7)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.set_ylabel('Précipitations (mm)')
        ax.set_title('Précipitations Moyennes')
        ax.grid(True, alpha=0.3)
        
        # NDVI
        ax = axes[0, 1]
        ax.plot(range(1, 13), monthly_avg['ndvi'], 
               marker='o', linewidth=2, color='green')
        ax.fill_between(range(1, 13), 
                        monthly_avg['ndvi'] - monthly_std['ndvi'],
                        monthly_avg['ndvi'] + monthly_std['ndvi'],
                        alpha=0.3, color='green')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.set_ylabel('NDVI')
        ax.set_title('NDVI Moyen')
        ax.grid(True, alpha=0.3)
        
        # NDWI
        ax = axes[1, 0]
        ax.plot(range(1, 13), monthly_avg['ndwi'], 
               marker='o', linewidth=2, color='blue')
        ax.fill_between(range(1, 13), 
                        monthly_avg['ndwi'] - monthly_std['ndwi'],
                        monthly_avg['ndwi'] + monthly_std['ndwi'],
                        alpha=0.3, color='blue')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.set_ylabel('NDWI')
        ax.set_title('NDWI Moyen')
        ax.grid(True, alpha=0.3)
        
        # LST
        ax = axes[1, 1]
        ax.plot(range(1, 13), monthly_avg['lst'], 
               marker='o', linewidth=2, color='red')
        ax.fill_between(range(1, 13), 
                        monthly_avg['lst'] - monthly_std['lst'],
                        monthly_avg['lst'] + monthly_std['lst'],
                        alpha=0.3, color='red')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.set_ylabel('LST (°C)')
        ax.set_title('Température Moyenne')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = config.PLOTS_DIR / f"{station_name}_climatology.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvegardé : {filename}")
        
        return fig


# ============================================================================
# BLOC DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU MODULE VISUALIZATION")
    print("=" * 70)
    print()
    
    # Station de test
    station_test = "MARRAKECH"
    
    # Charger les données d'analyse (générées par analysis.py)
    data_file = config.OUTPUT_DIR / f"{station_test}_with_anomalies.csv"
    
    if not data_file.exists():
        print(f"✗ Fichier non trouvé : {data_file}")
        print("Exécutez d'abord : python analysis.py")
        exit(1)
    
    print(f"Chargement des données : {data_file}")
    df_analysis = pd.read_csv(data_file, parse_dates=['date'], index_col='date')
    print(f"✓ {len(df_analysis)} lignes chargées")
    print()
    
    # Créer le générateur de rapports
    report_gen = ReportGenerator()
    
    # Générer les visualisations
    print("=" * 70)
    print("GÉNÉRATION DES VISUALISATIONS")
    print("=" * 70)
    print()
    
    # 1. Graphique de séries temporelles
    fig1 = report_gen.generate_timeseries_plot(df_analysis, station_test)
    print()
    
    # 2. Graphique de corrélation
    fig2 = report_gen.generate_correlation_plot(df_analysis, station_test)
    print()
    
    # 3. Climatologie mensuelle
    fig3 = report_gen.generate_monthly_climatology(df_analysis, station_test)
    print()
    
    print("=" * 70)
    print("✓ TOUS LES GRAPHIQUES GÉNÉRÉS AVEC SUCCÈS")
    print("=" * 70)
    print()
    print(f"Les graphiques sont disponibles dans : {config.PLOTS_DIR}")
    print()
    print("Fichiers générés :")
    print(f"  - {station_test}_timeseries.png")
    print(f"  - {station_test}_correlation.png")
    print(f"  - {station_test}_climatology.png")
    print()
    print("Le module visualization.py est prêt à être utilisé !")
    
    # Fermer les figures pour libérer la mémoire
    plt.close('all')