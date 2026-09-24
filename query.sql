WITH RECURSIVE
  -- Generate 10 grid points along X: x in [0.0, 10.0]
  x_steps AS (
    SELECT 0 AS ix, 0.0 AS x
    UNION ALL
    SELECT ix + 1, ROUND((ix + 1) * (10.0 / 9.0), 4)
    FROM x_steps WHERE ix < 9
  ),
  -- Generate 10 grid points along Y: y in [0.0, 1.0]
  y_steps AS (
    SELECT 0 AS iy, 0.0 AS y
    UNION ALL
    SELECT iy + 1, ROUND((iy + 1) * (1.0 / 9.0), 4)
    FROM y_steps WHERE iy < 9
  ),
  -- Flow Parameters: Top plate speed U = 1.0, Channel height H = 1.0
  params AS (
    SELECT 1.0 AS U, 1.0 AS H
  ),
  -- Build 2D vector mesh grid with unique cell_id (1 to 100)
  couette_mesh AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY x.ix, y.iy) AS cell_id,
      x.x,
      y.y,
      ROUND(p.U * (y.y / p.H), 4) AS u, -- u(y) = U * (y / H)
      0.0000 AS v                        -- v = 0 everywhere
    FROM x_steps x
    CROSS JOIN y_steps y
    CROSS JOIN params p
  )
SELECT 
  cell_id,
  x,
  y,
  u,
  v
FROM couette_mesh
ORDER BY cell_id;
