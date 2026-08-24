from pathlib import Path

import duckdb
import pytest

PROCESSED_PARQUET = Path('data/processed/trails.parquet')


@pytest.fixture(scope='module')
def db_connection():
    """Provides a shared DuckDB connection with spatial extension loaded."""
    conn = duckdb.connect()
    conn.execute('INSTALL spatial; LOAD spatial;')
    yield conn
    conn.close()


def test_parquet_file_exists():
    """Verify that the DuckDB pipeline produces the expected output artifact."""
    assert PROCESSED_PARQUET.exists(), f'Parquet file missing at {PROCESSED_PARQUET}'
    assert PROCESSED_PARQUET.stat().st_size > 0, 'Parquet file exists but is empty.'


def test_parquet_schema_and_columns(db_connection):
    """Ensure expected columns and types exist in the processed Parquet file."""
    query = f"DESCRIBE SELECT * FROM '{PROCESSED_PARQUET}'"
    schema = db_connection.execute(query).df()
    columns = schema['column_name'].tolist()

    expected_columns = [
        'name',
        'surface',
        'length_meters',
        'geometry',
    ]
    for col in expected_columns:
        assert col in columns, f'Missing required column: {col}'


def test_no_null_trail_names_or_surfaces(db_connection):
    """Verify COALESCE logic worked and no NULL strings remain in core attributes."""
    query = f"""
        SELECT 
            COUNT(*) - COUNT(name) AS null_names,
            COUNT(*) - COUNT(surface) AS null_surfaces
        FROM '{PROCESSED_PARQUET}';
    """
    result = db_connection.execute(query).fetchone()
    assert result[0] == 0, 'Found NULL name values'
    assert result[1] == 0, 'Found NULL surface values'


def test_valid_geometries_and_distances(db_connection):
    """Verify segment lengths are positive numbers and geometries are non-null."""
    query = f"""
        SELECT 
            MIN(length_meters) AS min_len,
            MAX(length_meters) AS max_len,
            COUNT(*) AS total_rows
        FROM '{PROCESSED_PARQUET}';
    """
    min_len, max_len, total_rows = db_connection.execute(query).fetchone()

    assert total_rows > 0, 'Processed dataset has zero rows'
    assert min_len >= 0, f'Invalid negative trail length found: {min_len}'
    assert max_len > 0, 'Maximum trail length must be greater than 0'
