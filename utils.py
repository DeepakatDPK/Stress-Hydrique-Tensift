"""
Fonctions utilitaires pour le projet
Contient notamment la conversion de coordonnées Lambert Maroc vers WGS84
"""

from pyproj import Transformer
import config


def convert_lambert_to_wgs84(x_km, y_km):
    """
    Convertit des coordonnées du système Lambert Maroc Nord (EPSG:26191) 
    vers le système WGS84 (EPSG:4326).
    
    Le système Lambert Maroc Nord utilise des coordonnées en kilomètres,
    donc nous devons d'abord les convertir en mètres.
    
    Args:
        x_km (float): Coordonnée X en kilomètres (Lambert Maroc Nord)
        y_km (float): Coordonnée Y en kilomètres (Lambert Maroc Nord)
    
    Returns:
        tuple: (longitude, latitude) en degrés décimaux (WGS84)
    
    Example:
        >>> lon, lat = convert_lambert_to_wgs84(250.0, 110.0)
        >>> print(f"Longitude: {lon:.6f}, Latitude: {lat:.6f}")
    """
    # Conversion des kilomètres en mètres
    x_meters = x_km * 1000
    y_meters = y_km * 1000
    
    # Créer le transformateur de coordonnées
    # EPSG:26191 = Lambert Conformal Conic Maroc Nord
    # EPSG:4326 = WGS84 (latitude/longitude)
    transformer = Transformer.from_crs(
        config.MOROCCO_EPSG,
        config.WGS84_EPSG,
        always_xy=True  # Garantit l'ordre (x, y) = (lon, lat)
    )
    
    # Transformation
    longitude, latitude = transformer.transform(x_meters, y_meters)
    
    return longitude, latitude


def validate_coordinates(station_name, station_info):
    """
    Valide et affiche les coordonnées converties d'une station.
    
    Args:
        station_name (str): Nom de la station
        station_info (dict): Dictionnaire avec les clés 'x', 'y', 'z'
    
    Returns:
        dict: Informations complètes avec coordonnées WGS84 ajoutées
    """
    x_km = station_info['x']
    y_km = station_info['y']
    
    lon, lat = convert_lambert_to_wgs84(x_km, y_km)
    
    result = station_info.copy()
    result['longitude'] = lon
    result['latitude'] = lat
    
    return result


# ============================================================================
# BLOC DE TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DE LA CONVERSION DE COORDONNÉES")
    print("=" * 70)
    print()
    
    # Test avec la station MARRAKECH
    station_name = "MARRAKECH"
    station_data = config.STATIONS_METADATA[station_name]
    
    print(f"Station: {station_name}")
    print(f"Coordonnées Lambert Maroc Nord (km):")
    print(f"  X = {station_data['x']} km")
    print(f"  Y = {station_data['y']} km")
    print(f"  Altitude = {station_data['z']} m")
    print()
    
    lon, lat = convert_lambert_to_wgs84(station_data['x'], station_data['y'])
    
    print(f"Coordonnées WGS84 (degrés décimaux):")
    print(f"  Longitude = {lon:.6f}°")
    print(f"  Latitude = {lat:.6f}°")
    print()
    
    # Test pour toutes les stations
    print("=" * 70)
    print("CONVERSION DE TOUTES LES STATIONS")
    print("=" * 70)
    print()
    
    print(f"{'Station':<25} {'Lon (°)':<12} {'Lat (°)':<12} {'Alt (m)':<10}")
    print("-" * 70)
    
    for name, info in config.STATIONS_METADATA.items():
        lon, lat = convert_lambert_to_wgs84(info['x'], info['y'])
        print(f"{name:<25} {lon:<12.6f} {lat:<12.6f} {info['z']:<10}")
    
    print()
    print("✓ Conversion réussie pour toutes les stations")
    print("✓ Les coordonnées sont maintenant prêtes pour Google Earth Engine")