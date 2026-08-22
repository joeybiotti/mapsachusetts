SELECT
    COUNT(*) AS total_segments,
    ROUND(SUM(length_miles), 2) AS total_county_miles,
    ROUND(AVG(length_miles), 3) AS avg_segment_miles,
    ROUND(MAX(length_miles), 2) AS longest_segment_miles
FROM trails;
