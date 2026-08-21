import sys

from scripts.ingest import fetch_mass_county_trails
from scripts.logger import get_logger
from scripts.process import load_to_duckdb, process_data

logger = get_logger('main')


def main():
    logger.info('Starting pipeline execution...')

    # Fetch raw data from OSM
    logger.info('Step 1 of 3: Running ingestion...')
    fetch_mass_county_trails()

    # Process raw GeoJSON to DuckDB GeoParquet
    logger.info('Step 2 of 3: Cleaning GeoJSON data and converting to GeoParquet...')
    parquet_path = process_data()

    # Load GeoParquet data to DuckDB
    logger.info('Step 3 of 3: Running DuckDB processing...')
    load_to_duckdb(parquet_file=parquet_path, table_name='trails')

    logger.info('Pipeline execution complete. Parquet dataset is ready.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f'Pipeline failed: {e}')
        sys.exit(1)
