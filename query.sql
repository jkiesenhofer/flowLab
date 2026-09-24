SELECT *
FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY id) AS row_num
    FROM simulation_data
) AS subquery
WHERE row_num BETWEEN 7 AND 11;

