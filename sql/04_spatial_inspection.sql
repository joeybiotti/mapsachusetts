-- Inspects DuckDB spatial geometry types and bounding boxes
INSTALL spatial;
LOAD spatial;

SELECT
    name,
    surface,
    ROUND(length_miles, 2) AS miles,
    ST_GeometryType(geom) AS geom_type,
    ST_AsText(ST_Envelope(geom)) AS segment_bbox
FROM trails
WHERE name != 'Unnamed Trail'
ORDER BY length_miles DESC
LIMIT 5;