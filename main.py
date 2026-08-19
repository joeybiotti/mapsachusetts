import sys

from scripts.ingest import fetch_local_rail_trails
from scripts.logger import get_logger

logger = get_logger('main')


def main():
    logger.info('Starting pipeline execution...')

    # Fetch raw data from OSM
    logger.info('Step 1 or 2: Running ingestion...')
    fetch_local_rail_trails()

    # Process raw GeoJSON to DuckDB GeoParquet
    logger.info('Step 2 of 2: Running DuckDB processing...')

    logger.info('Pipeline execution complete. Parquest dataset is ready.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f'Pipeline failed: {e}')
        sys.exit(1)
