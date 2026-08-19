from pathlib import Path

import duckdb

from scripts.logger import get_logger

logger = get_logger('process')

RAW_FILE = Path('data/raw/rail_trails.geojson')
PROCESSED_DIR = Path('data/processed')
PROCESSED_PARQUET = PROCESSED_DIR / 'rail_trails.parquet'


def process_geojson_to_parquet():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f'Loading {RAW_FILE} into DuckDB...')

    # Initialize DuckDB
    conn = duckdb.connect()

    # Load spatial extention
    conn.execute('INSTALL spatial; LOAD spatial;')

    # Ingest, clean attributes, and compute path lengths
    query = f"""
    CREATE TABLE rail_trails AS
        SELECT
            COALESCE(name, 'Unnamed Trail/Path') AS trail_name,
            COALESCE(surface, 'unknown') AS surface_type,
            COALESCE(smoothness, 'unknown') AS smoothness,
            -- Calculate segment length in meters directly in SQL
            ROUND(ST_Length(geom), 2) AS length_meters,
            geom
        FROM ST_Read('{RAW_FILE}')
        WHERE geom IS NOT NULL;
    """
    conn.execute(query)

    # Export directly to compressed Parquet format
    logger.info(f'Exporting to GeoParquet: {PROCESSED_PARQUET}')
    conn.execute(f"""
                 COPY rail_trails TO '{PROCESSED_PARQUET}' (FORMAT PARQUET);
    """)

    # Verification printout
    summary = conn.execute("""
        SELECT 
            COUNT(*) AS total_segments,
            ROUND(SUM(length_meters) / 1000.0, 2) AS total_km
        FROM rail_trails;
        """).fetchone()

    logger.info(
        f'Success! Processed {summary[0]} segments, totaling {summary[1]} km of trails. '
    )


if __name__ == '__main__':
    process_geojson_to_parquet()
