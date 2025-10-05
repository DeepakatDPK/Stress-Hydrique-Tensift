"""
Script principal du projet de détection du stress hydrique
Orchestre l'analyse complète pour toutes les stations du bassin du Tensift
"""

import config
from precipitation import PrecipitationManager
from gee_data import SatelliteDataManager
from analysis import StressAnalysis
from visualization import ReportGenerator
from datetime import datetime
import time


def main():
    """
    Fonction principale qui orchestre tout le pipeline d'analyse.
    """
    print("=" * 80)
    print(" " * 15 + "PROJET DE DÉTECTION DU STRESS HYDRIQUE")
    print(" " * 15 + "Bassin du Tensift - Maroc")
    print("=" * 80)
    print()
    
    # Configuration de l'analyse
    print("CONFIGURATION")
    print("-" * 80)
    print(f"Période d'analyse : {config.ANALYSIS_PERIOD[0]} à {config.ANALYSIS_PERIOD[1]}")
    print(f"Nombre de stations : {len(config.STATIONS_METADATA)}")
    print(f"Rayon d'analyse : {config.BUFFER_RADIUS}m autour de chaque station")
    print()
    
    # Demander confirmation pour l'analyse complète
    print("⚠ ATTENTION : L'analyse complète (1998-2019) peut prendre plusieurs heures")
    print("  - Environ 5-10 minutes par station")
    print("  - Total estimé : 1-2 heures pour 12 stations")
    print()
    
    mode = input("Choisissez le mode d'exécution :\n"
                 "  1 - TEST RAPIDE (2018-2019, 1 station : MARRAKECH)\n"
                 "  2 - ANALYSE PARTIELLE (2015-2019, toutes les stations)\n"
                 "  3 - ANALYSE COMPLÈTE (1998-2019, toutes les stations)\n"
                 "Votre choix (1/2/3) : ").strip()
    
    # Définir les paramètres selon le mode
    if mode == "1":
        stations_to_process = ["MARRAKECH"]
        start_year = 2018
        end_year = 2019
        print("\n→ Mode TEST RAPIDE sélectionné")
    elif mode == "2":
        stations_to_process = list(config.STATIONS_METADATA.keys())
        start_year = 2015
        end_year = 2019
        print("\n→ Mode ANALYSE PARTIELLE sélectionné")
    elif mode == "3":
        stations_to_process = list(config.STATIONS_METADATA.keys())
        start_year = 1998
        end_year = 2019
        print("\n→ Mode ANALYSE COMPLÈTE sélectionné")
    else:
        print("\n✗ Choix invalide. Mode TEST RAPIDE par défaut.")
        stations_to_process = ["MARRAKECH"]
        start_year = 2018
        end_year = 2019
    
    print(f"Stations à traiter : {', '.join(stations_to_process)}")
    print(f"Période : {start_year}-{end_year}")
    print()
    
    input("Appuyez sur Entrée pour continuer...")
    print()
    
    # Horodatage de début
    start_time = time.time()
    
    # ========================================================================
    # INITIALISATION DES GESTIONNAIRES
    # ========================================================================
    
    print("=" * 80)
    print("PHASE 1 : INITIALISATION")
    print("=" * 80)
    print()
    
    print("Initialisation du gestionnaire de précipitations...")
    precip_manager = PrecipitationManager(config.RAIN_DATA_PATH)
    
    print("Initialisation du gestionnaire de données satellitaires...")
    sat_manager = SatelliteDataManager(project_id='votre-project-id')
    
    print("Initialisation du générateur de rapports...")
    report_gen = ReportGenerator()
    
    print()
    print("✓ Tous les gestionnaires sont initialisés")
    print()
    
    # ========================================================================
    # BOUCLE PRINCIPALE SUR LES STATIONS
    # ========================================================================
    
    total_stations = len(stations_to_process)
    results_summary = []
    
    for idx, station_name in enumerate(stations_to_process, 1):
        station_start_time = time.time()
        
        print("=" * 80)
        print(f"PHASE 2 : ANALYSE DE LA STATION {idx}/{total_stations} - {station_name}")
        print("=" * 80)
        print()
        
        try:
            # Créer l'objet d'analyse
            analysis = StressAnalysis(station_name)
            print()
            
            # Exécuter l'analyse historique
            print(f"Extraction des données historiques ({start_year}-{end_year})...")
            df_results = analysis.run_historical_analysis(
                precip_manager,
                sat_manager,
                start_year=start_year,
                end_year=end_year
            )
            
            # Calculer les anomalies
            print("Calcul des anomalies (Z-scores)...")
            df_with_anomalies = analysis.calculate_anomalies()
            
            # Identifier les périodes de stress
            stress_periods = analysis.get_stress_periods(threshold=-1.5)
            n_stress = len(stress_periods)
            
            print(f"✓ Analyse terminée : {n_stress} périodes de stress détectées")
            print()
            
            # ================================================================
            # GÉNÉRATION DES VISUALISATIONS
            # ================================================================
            
            print("=" * 80)
            print(f"PHASE 3 : VISUALISATIONS - {station_name}")
            print("=" * 80)
            print()
            
            # Graphique de séries temporelles
            report_gen.generate_timeseries_plot(df_with_anomalies, station_name)
            
            # Graphique de corrélation
            report_gen.generate_correlation_plot(df_with_anomalies, station_name)
            
            # Climatologie mensuelle
            report_gen.generate_monthly_climatology(df_with_anomalies, station_name)
            
            print()
            
            # Calcul du temps d'exécution pour cette station
            station_elapsed = time.time() - station_start_time
            
            # Ajouter au résumé
            results_summary.append({
                'station': station_name,
                'total_months': len(df_results),
                'valid_data': df_results['ndvi'].notna().sum(),
                'stress_periods': n_stress,
                'time_seconds': station_elapsed
            })
            
            print(f"✓ Station {station_name} traitée en {station_elapsed/60:.1f} minutes")
            print()
            
        except Exception as e:
            print(f"✗ ERREUR lors du traitement de {station_name} : {e}")
            print()
            results_summary.append({
                'station': station_name,
                'error': str(e)
            })
            continue
    
    # ========================================================================
    # RAPPORT FINAL
    # ========================================================================
    
    total_elapsed = time.time() - start_time
    
    print()
    print("=" * 80)
    print("RAPPORT FINAL")
    print("=" * 80)
    print()
    
    print(f"Temps total d'exécution : {total_elapsed/60:.1f} minutes ({total_elapsed/3600:.2f} heures)")
    print(f"Stations traitées : {len(results_summary)}")
    print()
    
    print("RÉSUMÉ PAR STATION :")
    print("-" * 80)
    print(f"{'Station':<25} {'Mois':<10} {'Données':<10} {'Stress':<10} {'Temps':<10}")
    print("-" * 80)
    
    for result in results_summary:
        if 'error' in result:
            print(f"{result['station']:<25} ERREUR : {result['error']}")
        else:
            station = result['station']
            months = result['total_months']
            valid = result['valid_data']
            stress = result['stress_periods']
            time_min = result['time_seconds'] / 60
            print(f"{station:<25} {months:<10} {valid:<10} {stress:<10} {time_min:<10.1f}")
    
    print("-" * 80)
    print()
    
    print("FICHIERS GÉNÉRÉS :")
    print(f"  - Données CSV : {config.OUTPUT_DIR}")
    print(f"  - Graphiques : {config.PLOTS_DIR}")
    print(f"  - Cartes : {config.MAPS_DIR}")
    print()
    
    print("=" * 80)
    print("✓ ANALYSE TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print()
    print("Le projet est complet ! Consultez le dossier output/ pour les résultats.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Analyse interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n✗ ERREUR FATALE : {e}")
        import traceback
        traceback.print_exc()