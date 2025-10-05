"""
Module de gestion des données satellitaires via Google Earth Engine
Gère l'acquisition et le calcul des indices de végétation et d'humidité
"""

import ee
import config
from utils import convert_lambert_to_wgs84


class SatelliteDataManager:
    """
    Gestionnaire des données satellitaires via Google Earth Engine.
    Calcule les indices NDVI, NDWI et LST pour les stations du bassin du Tensift.
    """
    
    def __init__(self, project_id='votre-project-id'):
        """
        Initialise la connexion à Google Earth Engine.
        
        Args:
            project_id (str): ID du projet Google Cloud
        """
        print("=" * 70)
        print("INITIALISATION DE GOOGLE EARTH ENGINE")
        print("=" * 70)
        print()
        
        try:
            # Authentification (à faire une seule fois)
            # Décommenter la ligne suivante lors de la première utilisation
            # ee.Authenticate()
            
            # Initialisation avec le project ID
            ee.Initialize(project=project_id)
            print(f"✓ Connexion à GEE réussie (Project: {project_id})")
            self.initialized = True
            
        except Exception as e:
            print(f"✗ Erreur lors de l'initialisation de GEE : {e}")
            print()
            print("SOLUTION :")
            print("1. Décommentez la ligne 'ee.Authenticate()' dans le code")
            print("2. Exécutez à nouveau le script")
            print("3. Suivez les instructions pour vous authentifier")
            print("4. Une fois authentifié, recommentez 'ee.Authenticate()'")
            self.initialized = False
            raise
        
        print()
    
    def _create_roi(self, station_info, buffer_radius=None):
        """
        Crée une région d'intérêt (ROI) autour d'une station.
        
        Args:
            station_info (dict): Dictionnaire avec les coordonnées 'x', 'y' (en km)
            buffer_radius (int, optional): Rayon du buffer en mètres. 
                                          Utilise config.BUFFER_RADIUS par défaut
        
        Returns:
            ee.Geometry: Zone circulaire autour de la station
        """
        if buffer_radius is None:
            buffer_radius = config.BUFFER_RADIUS
        
        # Convertir les coordonnées Lambert en WGS84
        lon, lat = convert_lambert_to_wgs84(station_info['x'], station_info['y'])
        
        # Créer un point GEE
        point = ee.Geometry.Point([lon, lat])
        
        # Créer un buffer circulaire autour du point
        roi = point.buffer(buffer_radius)
        
        return roi
    
    def _get_monthly_composite(self, year, month, collection_name, roi):
        """
        Crée un composite mensuel sans nuages pour une collection donnée.
        
        Args:
            year (int): Année
            month (int): Mois (1-12)
            collection_name (str): Nom de la collection ('sentinel2' ou 'modis_lst')
            roi (ee.Geometry): Région d'intérêt
        
        Returns:
            ee.Image: Image composite du mois
        """
        # Définir les dates de début et fin du mois
        start_date = f"{year}-{month:02d}-01"
        
        # Calculer le dernier jour du mois
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        if collection_name == 'sentinel2':
            # Collection Sentinel-2 Surface Reflectance
            collection = ee.ImageCollection(config.GEE_COLLECTIONS['sentinel2']) \
                .filterBounds(roi) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 
                                    config.CLOUD_COVER_THRESHOLD))
            
            # Créer un composite médiane (robuste aux outliers)
            composite = collection.median().clip(roi)
            
        elif collection_name == 'modis_lst':
            # Collection MODIS Land Surface Temperature
            collection = ee.ImageCollection(config.GEE_COLLECTIONS['modis_lst']) \
                .filterBounds(roi) \
                .filterDate(start_date, end_date)
            
            # Sélectionner la bande de température de surface diurne
            # LST_Day_1km est en Kelvin * 0.02, il faut la convertir en Celsius
            composite = collection.select('LST_Day_1km').median().clip(roi)
            
        else:
            raise ValueError(f"Collection inconnue : {collection_name}")
        
        return composite
    
    def _calculate_ndvi(self, image):
        """
        Calcule le NDVI (Normalized Difference Vegetation Index).
        NDVI = (NIR - RED) / (NIR + RED)
        
        Args:
            image (ee.Image): Image Sentinel-2
        
        Returns:
            ee.Image: Image NDVI (valeurs entre -1 et 1)
        """
        nir = config.SENTINEL_BANDS['nir']  # B8
        red = config.SENTINEL_BANDS['red']  # B4
        
        ndvi = image.normalizedDifference([nir, red]).rename('NDVI')
        return ndvi
    
    def _calculate_ndwi(self, image):
        """
        Calcule le NDWI (Normalized Difference Water Index).
        NDWI = (GREEN - NIR) / (GREEN + NIR)
        
        Args:
            image (ee.Image): Image Sentinel-2
        
        Returns:
            ee.Image: Image NDWI (valeurs entre -1 et 1)
        """
        green = config.SENTINEL_BANDS['green']  # B3
        nir = config.SENTINEL_BANDS['nir']      # B8
        
        ndwi = image.normalizedDifference([green, nir]).rename('NDWI')
        return ndwi
    
    def _convert_lst_to_celsius(self, lst_image):
        """
        Convertit la température de surface MODIS en degrés Celsius.
        LST_Day_1km est en Kelvin * 0.02
        
        Args:
            lst_image (ee.Image): Image MODIS LST
        
        Returns:
            ee.Image: Image LST en Celsius
        """
        # Conversion : (Kelvin * 0.02) * 0.02 - 273.15
        lst_celsius = lst_image.multiply(0.02).subtract(273.15).rename('LST')
        return lst_celsius
    
    def get_monthly_indices(self, year, month, station_info):
        """
        Calcule les indices moyens (NDVI, NDWI, LST) pour un mois donné
        autour d'une station.
        
        Args:
            year (int): Année
            month (int): Mois (1-12)
            station_info (dict): Dictionnaire avec les coordonnées de la station
        
        Returns:
            dict: Dictionnaire avec les valeurs moyennes des indices
                  {'ndvi': float, 'ndwi': float, 'lst': float}
                  Retourne None pour une valeur si elle n'est pas disponible
        """
        if not self.initialized:
            raise RuntimeError("GEE n'est pas initialisé")
        
        # Créer la région d'intérêt
        roi = self._create_roi(station_info)
        
        result = {}
        
        try:
            # 1. Obtenir le composite Sentinel-2
            s2_image = self._get_monthly_composite(year, month, 'sentinel2', roi)
            
            # 2. Calculer NDVI
            ndvi = self._calculate_ndvi(s2_image)
            ndvi_stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=config.REDUCTION_SCALE,
                maxPixels=1e9
            ).getInfo()
            result['ndvi'] = ndvi_stats.get('NDVI', None)
            
            # 3. Calculer NDWI
            ndwi = self._calculate_ndwi(s2_image)
            ndwi_stats = ndwi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=config.REDUCTION_SCALE,
                maxPixels=1e9
            ).getInfo()
            result['ndwi'] = ndwi_stats.get('NDWI', None)
            
        except Exception as e:
            print(f"  ⚠ Erreur Sentinel-2 pour {year}-{month:02d}: {e}")
            result['ndvi'] = None
            result['ndwi'] = None
        
        try:
            # 4. Obtenir le composite MODIS LST
            modis_image = self._get_monthly_composite(year, month, 'modis_lst', roi)
            lst = self._convert_lst_to_celsius(modis_image)
            
            lst_stats = lst.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=1000,  # MODIS a une résolution de 1km
                maxPixels=1e9
            ).getInfo()
            result['lst'] = lst_stats.get('LST', None)
            
        except Exception as e:
            print(f"  ⚠ Erreur MODIS pour {year}-{month:02d}: {e}")
            result['lst'] = None
        
        return result
    
    def get_anomaly_map(self, index_name, year, month, basin_geometry):
        """
        Calcule une carte d'anomalie (Z-score) pour un indice donné.
        
        Args:
            index_name (str): Nom de l'indice ('ndvi', 'ndwi', 'lst')
            year (int): Année cible
            month (int): Mois cible (1-12)
            basin_geometry (ee.Geometry): Géométrie du bassin
        
        Returns:
            ee.Image: Image du Z-score spatial
        """
        # Cette méthode sera implémentée plus tard pour la visualisation
        # Elle nécessite de calculer la moyenne et l'écart-type historiques
        # sur l'ensemble du bassin
        raise NotImplementedError("Méthode à implémenter dans le module visualization")


# ============================================================================
# BLOC DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU MODULE GEE_DATA")
    print("=" * 70)
    print()
    
    # Initialiser le gestionnaire
    try:
        sat_manager = SatelliteDataManager(project_id='votre-project-id')
    except Exception as e:
        print("Impossible de continuer les tests sans authentification GEE")
        exit(1)
    
    # Station de test : MARRAKECH
    station_name = "MARRAKECH"
    station_info = config.STATIONS_METADATA[station_name]
    
    print("=" * 70)
    print(f"TEST : Extraction des indices pour {station_name}")
    print("=" * 70)
    print()
    
    # Convertir et afficher les coordonnées
    lon, lat = convert_lambert_to_wgs84(station_info['x'], station_info['y'])
    print(f"Station : {station_name}")
    print(f"Coordonnées : {lat:.6f}°N, {lon:.6f}°W")
    print(f"Rayon de la zone : {config.BUFFER_RADIUS}m")
    print()
    
    # Test pour Avril 2022 (période récente avec bonne couverture satellite)
    test_year = 2019
    test_month = 4
    
    print(f"Période de test : {test_year}-{test_month:02d}")
    print(f"Extraction des indices...")
    print()
    
    try:
        indices = sat_manager.get_monthly_indices(test_year, test_month, station_info)
        
        print("=" * 70)
        print("RÉSULTATS")
        print("=" * 70)
        print()
        
        print(f"NDVI (Santé de la végétation) : {indices['ndvi']:.4f}" if indices['ndvi'] else "NDVI : Non disponible")
        print(f"NDWI (Humidité de la végétation) : {indices['ndwi']:.4f}" if indices['ndwi'] else "NDWI : Non disponible")
        print(f"LST (Température de surface) : {indices['lst']:.2f}°C" if indices['lst'] else "LST : Non disponible")
        
        print()
        print("=" * 70)
        print("✓ TEST RÉUSSI")
        print("=" * 70)
        print()
        print("Le module gee_data.py est prêt à être utilisé !")
        
    except Exception as e:
        print(f"✗ Erreur lors de l'extraction : {e}")
        print()
        print("Vérifiez que :")
        print("1. Vous êtes bien authentifié sur GEE")
        print("2. Votre project ID est correct")
        print("3. Vous avez accès aux collections Sentinel-2 et MODIS")