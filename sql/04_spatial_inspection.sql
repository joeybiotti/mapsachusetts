-- Inspects DuckDB spatial geometry types and bounding boxes
INSTALL spatial;
LOAD spatial;

SELECT
    name,
    surface,
    ROUND(length_miles, 2) AS miles,
    ST_GeometryType(geometry) AS geom_type,
    ST_AsText(ST_Envelope(geometry)) AS segment_bbox
FROM trails
WHERE name != 'Unnamed Trail'
ORDER BY length_miles DESC
LIMIT 5;