"""
Création d'une carte interactive avec Folium
Montre les stations avec leur niveau de stress et caractéristiques
"""

import folium
from folium import plugins
import pandas as pd
import config
from utils import convert_lambert_to_wgs84


def create_interactive_map():
    """Crée une carte interactive Folium avec toutes les stations."""
    
    print("=" * 80)
    print("CRÉATION DE LA CARTE INTERACTIVE")
    print("=" * 80)
    print()
    
    # Charger les données de comparaison si disponibles
    summary_file = config.OUTPUT_DIR / "stations_comparison_summary.csv"
    
    if summary_file.exists():
        df_summary = pd.read_csv(summary_file)
        print(f"Données de comparaison chargées: {len(df_summary)} stations")
    else:
        print("⚠ Fichier de comparaison non trouvé. Exécutez d'abord advanced_analysis.py")
        df_summary = None
    
    # Créer la carte centrée sur le bassin du Tensift
    center_lat = 31.4
    center_lon = -8.2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Ajouter différents fonds de carte
    # folium.TileLayer('Stamen Terrain', name='Terrain').add_to(m)
    # folium.TileLayer('CartoDB positron', name='Clair').add_to(m)
    # folium.TileLayer('Stamen Toner', name='Contraste').add_to(m)
    
    print("\nAjout des marqueurs de stations...")
    
    # Ajouter les marqueurs pour chaque station
    for station_name, station_info in config.STATIONS_METADATA.items():
        # Convertir les coordonnées
        lon, lat = convert_lambert_to_wgs84(station_info['x'], station_info['y'])
        
        # Récupérer les statistiques si disponibles
        if df_summary is not None:
            station_row = df_summary[df_summary['station'] == station_name]
            
            if not station_row.empty:
                precip_mean = station_row['precip_mean'].values[0]
                ndvi_mean = station_row['ndvi_mean'].values[0]
                lst_mean = station_row['lst_mean'].values[0]
                stress_count = int(station_row['stress_count'].values[0])
                cluster = int(station_row['cluster'].values[0]) if 'cluster' in station_row.columns else 0
            else:
                precip_mean = ndvi_mean = lst_mean = stress_count = cluster = None
        else:
            precip_mean = ndvi_mean = lst_mean = stress_count = cluster = None
        
        # Déterminer la couleur en fonction du niveau de stress
        if stress_count is not None:
            if stress_count == 0:
                color = 'green'
                status = 'Faible'
            elif stress_count <= 2:
                color = 'lightgreen'
                status = 'Modéré'
            elif stress_count <= 5:
                color = 'orange'
                status = 'Élevé'
            else:
                color = 'red'
                status = 'Très élevé'
        else:
            color = 'gray'
            status = 'Indéterminé'
        
        # Déterminer la taille du marqueur en fonction de l'altitude
        altitude = station_info['z']
        if altitude < 500:
            radius = 8
        elif altitude < 1000:
            radius = 10
        else:
            radius = 12
        
        # Créer le popup avec informations détaillées
        if ndvi_mean is not None:
            popup_html = f"""
            <div style="font-family: Arial; width: 280px;">
                <h4 style="margin-bottom: 10px; color: #2c3e50;">{station_name}</h4>
                <hr style="margin: 5px 0;">
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>ID:</b></td><td>{station_info['id']}</td></tr>
                    <tr><td><b>Altitude:</b></td><td>{altitude} m</td></tr>
                    <tr><td><b>Coordonnées:</b></td><td>{lat:.4f}°N, {lon:.4f}°W</td></tr>
                    <tr><td colspan="2"><hr style="margin: 5px 0;"></td></tr>
                    <tr><td><b>Précip. moy:</b></td><td>{precip_mean:.1f} mm/mois</td></tr>
                    <tr><td><b>NDVI moyen:</b></td><td>{ndvi_mean:.3f}</td></tr>
                    <tr><td><b>Temp. moy:</b></td><td>{lst_mean:.1f}°C</td></tr>
                    <tr><td colspan="2"><hr style="margin: 5px 0;"></td></tr>
                    <tr>
                        <td><b>Stress:</b></td>
                        <td style="color: {color}; font-weight: bold;">{status}</td>
                    </tr>
                    <tr><td><b>Périodes:</b></td><td>{stress_count} mois</td></tr>
                    <tr><td><b>Cluster:</b></td><td>Groupe {cluster + 1}</td></tr>
                </table>
            </div>
            """
        else:
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="margin-bottom: 10px; color: #2c3e50;">{station_name}</h4>
                <hr style="margin: 5px 0;">
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>ID:</b></td><td>{station_info['id']}</td></tr>
                    <tr><td><b>Altitude:</b></td><td>{altitude} m</td></tr>
                    <tr><td><b>Coordonnées:</b></td><td>{lat:.4f}°N, {lon:.4f}°W</td></tr>
                    <tr><td colspan="2"><hr style="margin: 5px 0;"></td></tr>
                    <tr><td colspan="2"><i>Données en cours d'analyse</i></td></tr>
                </table>
            </div>
            """
        
        # Ajouter le marqueur
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{station_name} ({altitude}m)",
            color='black',
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
        
        # Ajouter un label avec le nom de la station
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 9px; font-weight: bold; 
                     color: white; text-shadow: 1px 1px 2px black;
                     white-space: nowrap;">
                    {station_name}
                </div>
            """)
        ).add_to(m)
        
        print(f"  - {station_name}: {lat:.4f}°N, {lon:.4f}°W - Stress: {status}")
    
    # Ajouter une légende personnalisée
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: auto; 
                background-color: white; z-index: 9999; 
                border: 2px solid grey; border-radius: 5px;
                padding: 10px; font-family: Arial; font-size: 12px;">
        <h4 style="margin-top: 0;">Niveau de Stress Hydrique</h4>
        <p style="margin: 5px 0;">
            <i class="fa fa-circle" style="color: green;"></i> Faible (0 périodes)<br>
            <i class="fa fa-circle" style="color: lightgreen;"></i> Modéré (1-2 périodes)<br>
            <i class="fa fa-circle" style="color: orange;"></i> Élevé (3-5 périodes)<br>
            <i class="fa fa-circle" style="color: red;"></i> Très élevé (>5 périodes)<br>
        </p>
        <hr style="margin: 8px 0;">
        <p style="margin: 5px 0; font-size: 10px;">
            <b>Taille du marqueur</b> = Altitude<br>
            Petit: <500m | Moyen: 500-1000m | Grand: >1000m
        </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Ajouter un contrôle de couches
    folium.LayerControl().add_to(m)
    
    # Ajouter une barre de mesure
    plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    
    # Ajouter la recherche de marqueurs
    #plugins.Search(
    #    layer=m,
    #    geom_type='Point',
    #    placeholder='Rechercher une station...',
    #    collapsed=False,
    #    search_label='name'
    #).add_to(m)
    
    # Ajouter un mini-map
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Sauvegarder la carte
    output_file = config.MAPS_DIR / "carte_interactive_stations.html"
    m.save(str(output_file))
    
    print()
    print("=" * 80)
    print("CARTE CRÉÉE AVEC SUCCÈS")
    print("=" * 80)
    print()
    print(f"Fichier: {output_file}")
    print()
    print("Fonctionnalités de la carte:")
    print("  - Cliquez sur un marqueur pour voir les détails")
    print("  - Changez le fond de carte en haut à droite")
    print("  - Utilisez la barre de recherche pour trouver une station")
    print("  - Mesurez des distances avec l'outil de mesure")
    print("  - Mini-carte dans le coin inférieur droit")
    print()
    
    return m


if __name__ == "__main__":
    create_interactive_map()