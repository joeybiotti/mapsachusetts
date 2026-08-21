from pathlib import Path

import geopandas as gdp
import osmnx as ox

from scripts.logger import get_logger

logger = get_logger('ingest')

PROJECT_ROOT = Path(__file__).parent.parent.resolve() if '__file__' in globals() else Path('.').resolve()
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'


def fetch_mass_county_trails():
    """Fetches statewide general trails (hiking, running, footpaths) across Middlesex County, MA, USA from OpenStreetMap via osmnx."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger.info('Fetching Middlesex County, MA, USA general trails from OpenStreetMap...')

    places = ['Middlesex County, MA, USA']

    tags = {'highway': ['path', 'footway', 'track', 'bridleway'], 'route': ['hiking', 'foot']}

    # Query OpenStreetsMap
    gdf: gdp.GeoDataFrame = ox.features_from_place(places, tags=tags)

    # Keep strict line segments geometries
    gdf = gdf[gdf.geometry.type.isin(['LineString', 'MultiLineString'])]

    # Filter out sidewalks and crossings
    if 'footway' in gdf.columns:
        gdf = gdf[~gdf['footway'].isin(['sidewalk', 'crossing'])]

    # Filter out private access segments
    if 'access' in gdf.columns:
        gdf = gdf[~gdf['access'].isin(['private', 'no'])]

    # Filter out informal trails/paths
    if 'informal' in gdf.columns:
        gdf = gdf[gdf['informal'] != 'yes']

    cols_to_keep = [
        'name',
        'highway',
        'surface',
        'sac_scale',  # Hiking difficulty scale
        'trail_visibility',  # Trail marking
        'operator',  # Managing body (e.g., DCR, Trustees, local land trust)
        'incline',
        'geometry',
    ]
    existing_cols = [c for c in cols_to_keep if c in gdf.columns]
    gdf = gdf[existing_cols].reset_index(drop=True)

    # Export raw GeoJSON
    output_file = RAW_DIR / 'mass_trails.geojson'
    gdf.to_file(output_file, driver='GeoJSON')

    size_mb = output_file.stat().st_size / (1024 * 1024)
    logger.info(f'Saved {len(gdf)} raw trail segments to {output_file} {size_mb} MB.')

    return output_file


if __name__ == '__main__':
    fetch_mass_county_trails()
