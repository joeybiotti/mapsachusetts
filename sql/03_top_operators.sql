-- Top managing entities (towns, state agencies, land trusts) by total mileage
SELECT
    operator,
    COUNT(*) AS total_segments,
    ROUND(SUM(length_miles), 2) AS managed_miles
FROM trails
WHERE operator != 'Unknown'
GROUP BY operator
ORDER BY managed_miles DESC
LIMIT 10;
