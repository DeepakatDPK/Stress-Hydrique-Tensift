"""
Configuration centrale du projet de détection du stress hydrique
Contient tous les paramètres, chemins et métadonnées des stations
"""

from pathlib import Path

# ============================================================================
# CHEMINS DES FICHIERS ET DOSSIERS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
MAPS_DIR = OUTPUT_DIR / "maps"
PLOTS_DIR = OUTPUT_DIR / "plots"

# Fichier de données de précipitations
RAIN_DATA_PATH = DATA_DIR / "rainfall_data.xlsx"

# ============================================================================
# MÉTADONNÉES DES STATIONS PLUVIOMÉTRIQUES
# ============================================================================
# Coordonnées en système Lambert Maroc Nord (EPSG:26191, en kilomètres)
# Structure: {nom_station: {'id': int, 'x': float, 'y': float, 'z': float}}

STATIONS_METADATA = {
    'ADAMNA': {
        'id': 50,
        'x': 92.9,      # Coordonnée X en km
        'y': 104.15,    # Coordonnée Y en km
        'z': 70         # Altitude en mètres
    },
    'AGHBALOU': {
        'id': 6193,
        'x': 276.15,
        'y': 83.05,
        'z': 1070
    },
    'AGOUNS': {
        'id': 902,
        'x': 271.45,
        'y': 69.65,
        'z': 2200
    },
    'AMENZAL': {
        'id': 1004,
        'x': 278.22,
        'y': 67.2,
        'z': 2230
    },
    'SIDI_HSSAIN_AMEZMEZ': {
        'id': 6826,
        'x': 229.1,
        'y': 70.17,
        'z': 1030
    },
    'CHICHAOUA': {
        'id': 2601,
        'x': 181.53,
        'y': 111.2,
        'z': 340
    },
    'ILOUDJANE': {
        'id': 4222,
        'x': 176.25,
        'y': 70.53,
        'z': 757
    },
    'MARRAKECH': {
        'id': 5229,
        'x': 250.0,
        'y': 110.0,
        'z': 460
    },
    'TAHANAOUT_RERAYA': {
        'id': 7512,
        'x': 255.9,
        'y': 80.4,
        'z': 925
    },
    'SIDI_BOUATHMANE': {
        'id': 6770,
        'x': 209.4,
        'y': 74.3,
        'z': 820
    },
    'TAFERIAT': {
        'id': 7352,
        'x': 291.25,
        'y': 107.5,
        'z': 760
    },
    'TTOURCHT': {
        'id': 8804,
        'x': 286.85,
        'y': 74.15,
        'z': 1650
    }
}

# ============================================================================
# PÉRIODE D'ANALYSE
# ============================================================================
# Format: 'AAAA-MM-JJ'
ANALYSIS_PERIOD = ('1998-01-01', '2019-07-31')

# ============================================================================
# PARAMÈTRES GOOGLE EARTH ENGINE
# ============================================================================

# Collections GEE
GEE_COLLECTIONS = {
    'sentinel2': 'COPERNICUS/S2_SR',              # Sentinel-2 Surface Reflectance
    'modis_lst': 'MODIS/061/MOD11A1',             # MODIS Land Surface Temperature
}

# Paramètres de filtrage
CLOUD_COVER_THRESHOLD = 20  # Pourcentage maximal de couverture nuageuse

# Bandes Sentinel-2 utilisées
SENTINEL_BANDS = {
    'blue': 'B2',
    'green': 'B3',
    'red': 'B4',
    'nir': 'B8',      # Near Infrared
    'swir': 'B11'     # Short Wave Infrared
}

# ============================================================================
# PARAMÈTRES D'ANALYSE
# ============================================================================

# Rayon de la zone tampon autour de chaque station (en mètres)
BUFFER_RADIUS = 5000  # 5 km

# Échelle de réduction pour l'extraction de données (en mètres)
REDUCTION_SCALE = 30  # 30m pour Sentinel-2

# Epsilon pour éviter la division par zéro dans les calculs de Z-score
EPSILON = 1e-6

# ============================================================================
# SYSTÈME DE COORDONNÉES
# ============================================================================

# Système de projection marocain (Lambert Maroc Nord)
MOROCCO_EPSG = 26191

# Système de coordonnées WGS84 (utilisé par GEE)
WGS84_EPSG = 4326