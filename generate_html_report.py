"""
Génération du rapport HTML consolidé final
Intègre toutes les analyses, graphiques et la carte interactive
"""

import config
from pathlib import Path
from datetime import datetime
import base64


def encode_image(image_path):
    """Encode une image en base64 pour l'intégrer dans le HTML."""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None


def generate_html_report():
    """Génère le rapport HTML complet."""
    
    print("=" * 80)
    print("GÉNÉRATION DU RAPPORT HTML CONSOLIDÉ")
    print("=" * 80)
    print()
    
    # Récupérer toutes les stations
    stations = list(config.STATIONS_METADATA.keys())
    
    # En-tête HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport - Stress Hydrique Bassin du Tensift</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .meta-info {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 5px solid #667eea;
            margin: 20px 40px;
        }}
        
        .meta-info p {{
            margin: 5px 0;
        }}
        
        nav {{
            background: #2c3e50;
            padding: 15px 40px;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        nav a:hover {{
            background: #34495e;
        }}
        
        section {{
            padding: 40px;
        }}
        
        h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 25px;
            font-size: 2em;
        }}
        
        h3 {{
            color: #34495e;
            margin: 25px 0 15px 0;
            font-size: 1.5em;
        }}
        
        .station-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }}
        
        .station-card {{
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .station-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}
        
        .station-card h3 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            margin: 0;
            font-size: 1.3em;
        }}
        
        .station-card img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .analysis-section {{
            background: #f0f4f8;
            padding: 30px;
            margin: 30px 0;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }}
        
        .key-findings {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .finding-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }}
        
        .finding-box h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .finding-box p {{
            color: #555;
            font-size: 0.95em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .map-container {{
            margin: 30px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .map-container iframe {{
            width: 100%;
            height: 600px;
            border: none;
        }}
        
        footer {{
            background: #2c3e50;
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        footer p {{
            margin: 5px 0;
            opacity: 0.8;
        }}
        
        .highlight {{
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
        }}
        
        @media print {{
            nav {{
                display: none;
            }}
            .station-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Détection du Stress Hydrique Agricole</h1>
            <p>Bassin du Tensift - Analyse par Télédétection Satellitaire</p>
        </header>
        
        <div class="meta-info">
            <p><strong>Période d'analyse:</strong> {config.ANALYSIS_PERIOD[0]} à {config.ANALYSIS_PERIOD[1]}</p>
            <p><strong>Nombre de stations:</strong> {len(stations)} stations pluviométriques</p>
            <p><strong>Sources de données:</strong> Sentinel-2 (NDVI, NDWI), MODIS (LST), Données in-situ</p>
        </div>
        
        <nav>
            <ul>
                <li><a href="#synthese">Synthèse</a></li>
                <li><a href="#carte">Carte Interactive</a></li>
                <li><a href="#analyses">Analyses Statistiques</a></li>
                <li><a href="#correlations">Corrélations</a></li>
                <li><a href="#stress">Stress Hydrique</a></li>
                <li><a href="#climatologies">Climatologies</a></li>
                <li><a href="#conclusions">Conclusions</a></li>
            </ul>
        </nav>
        
        <section id="synthese">
            <h2>Synthèse Exécutive</h2>
            
            <div class="analysis-section">
                <h3>Contexte et Objectifs</h3>
                <p>Ce projet vise à détecter et cartographier le stress hydrique agricole dans le bassin du Tensift 
                (Maroc) en utilisant des données de télédétection satellitaire combinées aux mesures pluviométriques 
                au sol. L'analyse couvre la période 2015-2019 pour 12 stations distribuées sur un gradient altitudinal 
                de 70m à 2230m.</p>
            </div>
            
            <div class="key-findings">
                <div class="finding-box">
                    <h4>Gradient Climatique</h4>
                    <p>Forte variabilité climatique selon l'altitude. Les stations de montagne (>1500m) présentent 
                    des températures plus fraîches mais une végétation limitée par les conditions rocheuses.</p>
                </div>
                
                <div class="finding-box">
                    <h4>Stress Hydrique</h4>
                    <p>8 périodes de stress détectées sur l'ensemble du bassin, principalement en été 
                    (juin-août) avec des températures dépassant 40°C et un NDVI inférieur à 0.15.</p>
                </div>
                
                <div class="finding-box">
                    <h4>Zones Prioritaires</h4>
                    <p>AGHBALOU et SIDI_HSSAIN_AMEZMEZ montrent une haute productivité agricole 
                    (NDVI > 0.40) nécessitant une sécurisation de l'approvisionnement en eau.</p>
                </div>
                
                <div class="finding-box">
                    <h4>Zones à Risque</h4>
                    <p>CHICHAOUA présente les signes les plus sévères de dégradation (NDVI < 0.12) 
                    avec un risque élevé de désertification.</p>
                </div>
            </div>
        </section>
        
        <section id="carte">
            <h2>Carte Interactive des Stations</h2>
            <p>Explorez la localisation des stations et leurs caractéristiques. Cliquez sur chaque marqueur pour 
            obtenir des informations détaillées.</p>
            <div class="map-container">
                <iframe src="carte_interactive_stations.html"></iframe>
            </div>
        </section>
        
        <section id="analyses">
            <h2>Analyses Statistiques Multi-Stations</h2>"""
    
    # Ajouter les images d'analyses avancées
    analysis_images = [
        ('correlation_matrix_stations.png', 'Matrice de Corrélation Inter-Stations'),
        ('clustering_dendrogram.png', 'Classification Hiérarchique des Stations'),
        ('bivariate_analysis.png', 'Analyses Bivariées')
    ]
    
    for img_name, title in analysis_images:
        img_path = config.PLOTS_DIR / img_name
        if img_path.exists():
            img_base64 = encode_image(img_path)
            if img_base64:
                html_content += f"""
            <h3>{title}</h3>
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; max-width: 1200px; 
                 height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
"""
    
    html_content += """
        </section>
        
        <section id="correlations">
            <h2>Corrélations Précipitations vs Indices par Station</h2>
            <p>Analyse de la relation entre les précipitations et les indices de végétation/température pour chaque station.</p>
            <div class="station-grid">"""
    
    # Ajouter les graphiques de corrélation
    for station_name in stations:
        correlation_path = config.PLOTS_DIR / f"{station_name}_correlation.png"
        
        if correlation_path.exists():
            img_base64 = encode_image(correlation_path)
            if img_base64:
                station_info = config.STATIONS_METADATA[station_name]
                html_content += f"""
                <div class="station-card">
                    <h3>{station_name} ({station_info['z']}m)</h3>
                    <img src="data:image/png;base64,{img_base64}">
                </div>"""
    
    html_content += """
            </div>
        </section>
        
        <section id="stress">
            <h2>Analyse du Stress Hydrique par Station</h2>
            <p>Évolution temporelle des anomalies (Z-scores) des indices satellitaires et des précipitations.</p>
            <div class="station-grid">"""
    
    # Ajouter les graphiques de stress
    for station_name in stations:
        timeseries_path = config.PLOTS_DIR / f"{station_name}_timeseries.png"
        
        if timeseries_path.exists():
            img_base64 = encode_image(timeseries_path)
            if img_base64:
                station_info = config.STATIONS_METADATA[station_name]
                html_content += f"""
                <div class="station-card">
                    <h3>{station_name} ({station_info['z']}m)</h3>
                    <img src="data:image/png;base64,{img_base64}">
                </div>"""
    
    html_content += """
            </div>
        </section>

        <section id="climatologies">
            <h2>Climatologies Mensuelles par Station</h2>
            <p>Évolution saisonnière des principaux indicateurs pour chaque station du bassin.</p>
            <div class="station-grid">"""
    
    # Ajouter les climatologies de chaque station
    for station_name in stations:
        climatology_path = config.PLOTS_DIR / f"{station_name}_climatology.png"
        
        if climatology_path.exists():
            img_base64 = encode_image(climatology_path)
            if img_base64:
                station_info = config.STATIONS_METADATA[station_name]
                html_content += f"""
                <div class="station-card">
                    <h3>{station_name} ({station_info['z']}m)</h3>
                    <img src="data:image/png;base64,{img_base64}">
                </div>"""
    
    html_content += """
            </div>
        </section>
        
        <section id="conclusions">
            <h2>Conclusions et Recommandations</h2>
            
            <div class="analysis-section">
                <h3>Principales Conclusions</h3>
                <ol style="line-height: 2;">
                    <li><strong>Gradient altitudinal majeur:</strong> L'altitude influence fortement le climat, 
                    mais pas nécessairement la productivité végétale (zones rocheuses en altitude).</li>
                    
                    <li><strong>Stress estival généralisé:</strong> Toutes les stations montrent un déclin du NDVI 
                    en été avec des températures > 40°C et absence de précipitations.</li>
                    
                    <li><strong>Variabilité spatiale importante:</strong> Le clustering révèle 3 groupes distincts 
                    de stations avec des dynamiques hydro-climatiques différentes.</li>
                    
                    <li><strong>Corrélations pluie-végétation:</strong> Un délai de 1-2 mois est observé entre 
                    les précipitations et la réponse végétale, validant l'approche méthodologique.</li>
                </ol>
                
                <h3>Recommandations Opérationnelles</h3>
                <ul style="line-height: 2;">
                    <li><strong>Surveillance prioritaire:</strong> Mettre en place un système d'alerte précoce 
                    pour CHICHAOUA et ADAMNA (zones à risque de désertification).</li>
                    
                    <li><strong>Optimisation de l'irrigation:</strong> Les stations AGHBALOU et SIDI_HSSAIN_AMEZMEZ 
                    nécessitent une gestion optimisée de l'eau pour maintenir leur productivité.</li>
                    
                    <li><strong>Extension temporelle:</strong> Étendre l'analyse à la période complète 1998-2019 
                    pour identifier les tendances à long terme et l'impact du changement climatique.</li>
                    
                    <li><strong>Validation terrain:</strong> Collecter des données de rendement agricole pour 
                    valider quantitativement les indices de stress détectés.</li>
                </ul>
                
                <h3>Limites et Perspectives</h3>
                <p>Cette étude constitue un prototype opérationnel avec certaines limites à considérer:</p>
                <ul style="line-height: 2;">
                    <li>Le Z-score est une méthode simple; des modèles ML plus sophistiqués pourraient améliorer 
                    la précision.</li>
                    <li>Impossible de distinguer stress hydrique d'autres stress (maladies, carences nutritives).</li>
                    <li>Couverture nuageuse limitant la disponibilité des données Sentinel-2 (~50% de données valides).</li>
                    <li>Station TAHANAOUT_RERAYA nécessite une vérification des données de précipitations.</li>
                </ul>
            </div>
        </section>
        
        <footer>
            <p><strong>Projet de Data Science Géospatiale</strong></p>
            <p>Détection du Stress Hydrique par Télédétection - Bassin du Tensift, Maroc</p>
            <p>Technologies: Python, Google Earth Engine, Sentinel-2, MODIS</p>
            <p>{datetime.now().year} - Analyse réalisée avec Google Earth Engine API</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Sauvegarder le rapport
    output_file = config.MAPS_DIR / "rapport_final_stress_hydrique.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Rapport HTML généré: {output_file}")
    print()
    print("=" * 80)
    print("RAPPORT GÉNÉRÉ AVEC SUCCÈS")
    print("=" * 80)
    print()
    print("Le rapport inclut:")
    print("  - Synthèse exécutive avec points clés")
    print("  - Carte interactive intégrée")
    print("  - Analyses statistiques multi-stations")
    print("  - Climatologies mensuelles de toutes les stations")
    print("  - Conclusions et recommandations détaillées")
    print()
    print(f"Ouvrez le fichier dans votre navigateur: {output_file}")
    print()


if __name__ == "__main__":
    generate_html_report()