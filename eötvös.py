import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# 1. Execute SQL Query with local Eötvös number field formulation
sql_query = """
WITH RECURSIVE
  -- Grid steps: x in [-3.0, 3.0] with 25 points
  x_steps AS (
    SELECT 0 AS ix, -3.0 AS x
    UNION ALL
    SELECT ix + 1, ROUND(-3.0 + (ix + 1) * (6.0 / 24.0), 4)
    FROM x_steps WHERE ix < 24
  ),
  -- Grid steps: y in [-4.0, 3.0] with 29 points
  y_steps AS (
    SELECT 0 AS iy, -4.0 AS y
    UNION ALL
    SELECT iy + 1, ROUND(-4.0 + (iy + 1) * (7.0 / 28.0), 4)
    FROM y_steps WHERE iy < 28
  ),
  -- Base physical parameters for Eötvös Number: Eo = (delta_rho * g * d^2) / sigma
  params AS (
    SELECT 
      1.0 AS Rx, 
      0.85 AS Ry, 
      2.5 AS Eo_base,      -- Global characteristic Eötvös number
      9.81 AS g,           -- Gravity
      1000.0 AS delta_rho  -- Density difference (fluid - gas)
  ),
  eotvos_calc AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY x.ix, y.iy) AS cell_id,
      x.x,
      y.y,
      p.Rx,
      p.Ry,
      p.Eo_base,
      ROUND(SQRT((x.x/p.Rx)*(x.x/p.Rx) + (y.y/p.Ry)*(y.y/p.Ry)), 4) AS r_eff,
      ROUND(SQRT(x.x * x.x + y.y * y.y), 4) AS r
    FROM x_steps x
    CROSS JOIN y_steps y
    CROSS JOIN params p
  ),
  eotvos_field AS (
    SELECT 
      cell_id, x, y, r_eff, r,
      -- Local Eötvös field Eo(x,y): scaled by local effective radius/curvature variations
      CASE 
        WHEN r_eff <= 1.0 THEN 0.0
        -- Downstream wake deformation alters effective local buoyancy vs surface tension balance
        WHEN y < -Ry THEN ROUND(Eo_base * (1.0 + 0.4 * EXP(-(x*x + (y + 1.5)*(y + 1.5)))), 4)
        -- Upstream flow with hydrostatic pressure gradients modifying effective local Eo
        ELSE ROUND(Eo_base * (1.0 + 0.3 * (Rx / (r + 0.1)) * COS(ATAN2(y, x))), 4)
      END AS Eo_local
    FROM eotvos_calc
  ),
  -- Trajectory simulation based on critical Eo threshold sliding
  particle_sim AS (
    SELECT 
      0 AS step,
      0.35 AS xp,
      2.5 AS yp,
      0.0 AS up,
      -0.8 AS vp,
      ATAN2(2.5/0.85, 0.35) AS theta,
      'APPROACHING' AS state
    UNION ALL
    SELECT 
      step + 1,
      -- Position update along interface governed by Eo stress distribution
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            1.0 * COS(theta - 0.06)
          ELSE xp + up * 0.05
        END, 4
      ) AS xp,
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            0.85 * SIN(theta - 0.06)
          ELSE yp + vp * 0.05
        END, 4
      ) AS yp,
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            -1.0 * SIN(theta)
          ELSE up + 4.0 * ((-1.0 * (1.5 / (xp*xp + yp*yp)) * (xp * yp / (xp*xp + yp*yp))) - up) * 0.05
        END, 4
      ) AS up,
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            0.85 * COS(theta)
          ELSE vp + 4.0 * ((-1.0 * (1.0 - 0.5 / SQRT(xp*xp + yp*yp))) - vp) * 0.05 - 0.2 * 0.05
        END, 4
      ) AS vp,
      CASE 
        WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN theta - 0.06
        ELSE theta
      END AS theta,
      CASE 
        WHEN theta <= -1.50 THEN 'DETACHED'
        WHEN SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 OR state = 'SLIDING' THEN 'SLIDING'
        ELSE 'APPROACHING'
      END AS state
    FROM particle_sim
    WHERE step < 75 AND yp > -3.5
  )
SELECT 
  ef.cell_id, ef.x, ef.y, ef.Eo_local,
  ps.step, ps.xp, ps.yp, ps.up, ps.vp, ps.state
FROM eotvos_field ef
LEFT JOIN particle_sim ps ON ef.cell_id = ps.step + 1
ORDER BY ef.cell_id;
"""

# Run SQL query in memory
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()
conn.close()

# 2. Process Data Grid
x_vals = sorted(list(set(row[1] for row in rows)))
y_vals = sorted(list(set(row[2] for row in rows)))

nx, ny = len(x_vals), len(y_vals)
X, Y = np.meshgrid(x_vals, y_vals)
Eo_grid = np.zeros((ny, nx))

particle_traj = []

for row in rows:
    cell_id, x, y, eo_local, step, xp, yp, up, vp, state = row
    ix = x_vals.index(x)
    iy = y_vals.index(y)
    Eo_grid[iy, ix] = eo_local
    if xp is not None:
        particle_traj.append((xp, yp, state))

px = [pt[0] for pt in particle_traj]
py = [pt[1] for pt in particle_traj]

# Mask interior of the bubble (r_eff <= 1.0)
R_mesh = np.sqrt(X**2 + (Y / 0.85)**2)
Eo_masked = np.ma.masked_where(R_mesh <= 1.0, Eo_grid)

# 3. Plotting the Eötvös Number Field & Trajectory
fig, ax = plt.subplots(figsize=(8, 9))

# Eötvös Field Heatmap
c = ax.pcolormesh(X, Y, Eo_masked, cmap='magma', shading='auto', alpha=0.85)
fig.colorbar(c, ax=ax, label='Local Eötvös Number ($Eo$)')

# Iso-Eötvös Contour lines
cs = ax.contour(X, Y, Eo_masked, levels=6, colors='white', linewidths=0.7, alpha=0.6)
ax.clabel(cs, inline=True, fontsize=8, fmt='Eo=%.1f')

# Draw Deformed Bubble Boundary Line (Interface)
theta_arr = np.linspace(0, 2 * np.pi, 300)
bx = 1.0 * np.cos(theta_arr)
by = 0.85 * np.sin(theta_arr)
ax.plot(bx, by, color='#00e676', lw=3, zorder=5, label='Bubble Interface ($r_{eff}=1.0$)')
ax.fill(bx, by, color='#111111', alpha=0.8, zorder=4)

# Plot Particle Trajectory along interface
ax.plot(px, py, color='cyan', linestyle='-', linewidth=3, zorder=8, label='Particle Trajectory')

# Key Interaction Points
ax.scatter([px[0]], [py[0]], color='yellow', edgecolors='black', s=110, zorder=10, label='Particle Approach')
ax.scatter([px[18]], [py[18]], color='orange', edgecolors='black', s=120, zorder=10, label='Film Contact')
ax.scatter([px[-1]], [py[-1]], color='red', edgecolors='black', s=110, zorder=10, label='Detachment into Wake')

# Annotations
ax.annotate('$Eo$-Controlled Sliding Path', xy=(px[28], py[28]), xytext=(px[28]+0.5, py[28]+0.2),
            arrowprops=dict(arrowstyle="->", color='cyan', lw=2), fontsize=10, fontweight='bold', color='cyan')

# Graph Layout Settings
ax.set_title('Hydrodynamic Field: Local Eötvös Number ($Eo$) & Interface Sliding', fontsize=11)
ax.set_xlabel('Horizontal Position $x$')
ax.set_ylabel('Vertical Position $y$')
ax.set_xlim(-3.0, 3.0)
ax.set_ylim(-4.0, 3.0)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.show()
