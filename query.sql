WITH random_select AS (
    SELECT 
        CAST(ABS(RANDOM()) % 100 + 1 AS INTEGER) AS cell_id
)
SELECT 
    cell_id, 
    'Original Value' AS description
FROM random_select

UNION ALL

SELECT 
    cell_id * cell_id AS cell_id, 
    'Squared Value' AS description
FROM random_select;
