-- Aggregates total mileage by surface type (dirt, paved, gravel, etc.)
SELECT
    surface,
    COUNT(*) AS segment_count,
    ROUND(SUM(length_miles), 2) AS total_miles,
    ROUND(
        SUM(length_miles) * 100.0 / SUM(SUM(length_miles)) OVER (),
        1
    ) AS pct_of_total
FROM trails
GROUP BY surface
ORDER BY total_miles DESC;
