import duckdb

conn = duckdb.connect()
conn.execute('INSTALL spatial; LOAD spatial;')

df = conn.execute("""
    SELECT 
        surface_type,
        COUNT(*) AS segment_count,
        ROUND(SUM(length_meters) / 1609.34, 2) AS total_miles
    FROM 'data/processed/rail_trails.parquet'
    GROUP BY surface_type
    ORDER BY total_miles DESC;
""").df()

print(df)
