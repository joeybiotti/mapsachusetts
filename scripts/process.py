from pathlib import Path

import duckdb
import geopandas as gpd

from scripts.logger import get_logger

logger = get_logger('process')

PROJECT_ROOT = Path(__file__).parent.parent.resolve() if '__file__' in globals() else Path('.').resolve()
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
DB_PATH = PROJECT_ROOT / 'mapsachusetts.duckdb'


def process_data():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_geojson = RAW_DIR / 'mass_trails.geojson'

    if not raw_geojson.exists():
        raise FileNotFoundError(f'Raw data not found at {raw_geojson}. Run ingest.py first.')

    logger.info(f'Reading raw GeoJSON from {raw_geojson}')
    gdf = gpd.read_file(raw_geojson)

    # Clean missing and null data
    if 'name' in gdf.columns:
        gdf['name'] = gdf['name'].fillna('Unnamed Trail')
    else:
        gdf['name'] = 'Unnamed Trail'

    if 'surface' in gdf.columns:
        gdf['surface'] = gdf['surface'].fillna('unspecified')

    if 'operator' in gdf.columns:
        gdf['operator'] = gdf['operator'].fillna('Unknown')

    # Reproject to MA State Plane (EPSG:26986) for precise linear distance measurements
    logger.info('Reprojecting geometries to EPSG:26986 (NAD83 / Massachusetts Mainland)...')
    gdf = gdf.to_crs(epsg=26986)

    # Calculate accurate length columns
    gdf['length_meters'] = gdf.geometry.length
    gdf['length_miles'] = gdf['length_meters'] / 1609.34

    # Save GeoParquet output
    parquet_path = PROCESSED_DIR / 'trails.parquet'
    logger.info(f'Writing cleaned GeoParquet to {parquet_path}...')

    # Write GeoDataFrame to GeoParquet file on disk
    gdf.to_parquet(parquet_path)

    # Load to DuckDB
    load_to_duckdb(parquet_path, table_name='trails')

    return parquet_path


def load_to_duckdb(parquet_path: Path, table_name: str = 'trails') -> None:
    """Load processed GeoParquet into DuckDB table with lock fallback."""
    try:
        # Set a 5-second config timeout so it doesn't hang indefinitely on locks
        conn = duckdb.connect(str(DB_PATH), config={'access_mode': 'READ_WRITE'})
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{parquet_path}'")
        conn.close()
        logger.info(f"Successfully updated table '{table_name}' in {DB_PATH}")
    except duckdb.IOException as e:
        logger.warning(f'Could not write to {DB_PATH} due to file lock: {e}')
        logger.warning(f'Parquet artifact successfully saved to {parquet_path}. Continuing...')


if __name__ == '__main__':
    parquet_path = process_data()
    load_to_duckdb(parquet_path=parquet_path, table_name='trails')
