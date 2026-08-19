from pathlib import Path
import osmnx as ox
from scripts.logger import get_logger

logger = get_logger('process')

RAW_DIR = Path('data/raw')
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_local_rail_trails():
    """ Fetches paved bike paths and multi-use rail trails across Middlesex/Metrowest directly from OpenStreetMap via osmnx. """
    logger.info('Fetching local rail trails via OpenStreetMap...')
    
    places = [
        'Acton, Massachusetts, USA',
        'Concord, Massachusetts, USA',
        'Hudson, Massachusetts, USA',
        'Maynard, Massachusetts, USA'
    ]
    
    tags = {'highway':['cycleway', 'path']}
    
    # Query OpenStreetMaps
    gdf = ox.features_from_place(places, tags=tags)
    
    # Keep strictly line segement paths
    gdf = gdf[gdf.geometry.type.isin(['LineString', 'MultiLineString'])]
    
    # Filter to essential columns
    cols_to_keep = ['name', 'surface', 'smoothness', 'geometry']
    existing_cols = [c for c in cols_to_keep if c in gdf.columns]
    gdf = gdf[existing_cols]
    
    # Reset multi-index for clean GeoJSON export
    gdf = gdf.reset_index(drop=True)
    
    # Save output
    output_file = RAW_DIR / 'rail_trails.geojson'
    gdf.to_file(output_file, driver='GeoJSON')
    
    size_mb = output_file.stat().st_size / (1024 * 1024)
    logger.info(f'File saved. Saved {len(gdf)} segments to {output_file} {size_mb:.2f} MB.')
    
if __name__ == '__main__':
    fetch_local_rail_trails()