from pathlib import Path
import duckdb
import geopandas as gpd
from scripts.logger import get_logger

logger = get_logger('process')

BASE_DIR = Path(__file__).parent.parent.resolve() if '__file__' in globals() else Path('.').resolve()
PROCESSED_DIR = BASE_DIR / 'data'/ 'processed'
DB_PATH = BASE_DIR / 'mapsachusetts.db'

def process_data():
    parquet_path = PROCESSED_DIR / 'trails.parquet'
    logger.info(f'Saved processed Parquet to {parquet_path}.')
    
    load_to_duckdb(parquet_path, table_name ='trails')
    
def load_to_duckdb(paquet_file: Path, table_name: str):
    """Loads a processed GeoParquet file into mapsachusetts.db"""
    logger.info(f'Updating table {table_name} in {DB_PATH}...')
    
    conn = duckdb.connect(str(DB_PATH))
    
    conn.execute('INSTALL spatial; LOAD spatial;')
    
    # Overwrite or create the table directly from Parquet output
    conn.execute(f"""
                 CREATE OR REPLACE TABLE {table_name} AS
                 SELECT * FROM read_parquet('{paquet_file}')
    """)
    
    count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
    conn.close()
    
    logger.info(f'Successfully loaded {count} rows into "{table_name}".')
    
if __name__ == '__main__':
    process_data()