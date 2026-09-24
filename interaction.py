import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# 1. Execute SQL Query with strict polar interface constraint during contact
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
  params AS (
    SELECT 1.0 AS U_rise, 1.0 AS Rx, 0.85 AS Ry
  ),
  buoyant_calc AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY x.ix, y.iy) AS cell_id,
      x.x,
      y.y,
      p.U_rise,
      p.Rx,
      p.Ry,
      ROUND(SQRT((x.x/p.Rx)*(x.x/p.Rx) + (y.y/p.Ry)*(y.y/p.Ry)), 4) AS r_eff,
      ROUND(SQRT(x.x * x.x + y.y * y.y), 4) AS r
    FROM x_steps x
    CROSS JOIN y_steps y
    CROSS JOIN params p
  ),
  buoyant_velocities AS (
    SELECT 
      cell_id, x, y, r_eff, r,
      CASE 
        WHEN r_eff <= 1.0 THEN 0.0
        WHEN y < -Ry THEN -0.8 * U_rise * (x / (Rx + ABS(y))) * EXP(-(x * x + (y + 1.5) * (y + 1.5)))
        ELSE -U_rise * (1.5 * (Rx * Rx) / (r * r)) * (x * y / (r * r))
      END AS u_raw,
      CASE 
        WHEN r_eff <= 1.0 THEN 0.0
        WHEN y < -Ry THEN -U_rise + 0.6 * U_rise * EXP(-(x * x) / (0.8 * Rx)) * EXP(0.4 * y)
        ELSE -U_rise * (1.0 - 0.5 * (Rx / r) + 1.5 * (Rx * Rx * y * y) / (r * r * r * r))
      END AS v_raw
    FROM buoyant_calc
  ),
  -- Trajectory Simulation: Exact interface sliding along r_eff = 1.0
  particle_sim AS (
    -- Start: Approaching from top-right
    SELECT 
      0 AS step,
      0.35 AS xp,
      2.5 AS yp,
      0.0 AS up,
      -0.8 AS vp,
      ATAN2(2.5/0.85, 0.35) AS theta, -- Polar angle
      'APPROACHING' AS state
    UNION ALL
    SELECT 
      step + 1,
      -- Position Update
      ROUND(
        CASE 
          -- ON INTERFACE: Constrain x, y strictly to bubble boundary (r_eff = 1.0)
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            1.0 * COS(theta - 0.06)
          WHEN state = 'DETACHED' THEN xp + up * 0.05
          ELSE xp + up * 0.05
        END, 4
      ) AS xp,
      ROUND(
        CASE 
          -- ON INTERFACE: Constrain y strictly to 0.85 * sin(theta)
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            0.85 * SIN(theta - 0.06)
          WHEN state = 'DETACHED' THEN yp + vp * 0.05
          ELSE yp + vp * 0.05
        END, 4
      ) AS yp,
      -- Velocity Update
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            -1.0 * SIN(theta) -- Tangential vector u_theta
          ELSE up + 4.0 * ((-1.0 * (1.5 / (xp*xp + yp*yp)) * (xp * yp / (xp*xp + yp*yp))) - up) * 0.05
        END, 4
      ) AS up,
      ROUND(
        CASE 
          WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN
            0.85 * COS(theta) -- Tangential vector v_theta
          ELSE vp + 4.0 * ((-1.0 * (1.0 - 0.5 / SQRT(xp*xp + yp*yp))) - vp) * 0.05 - 0.2 * 0.05
        END, 4
      ) AS vp,
      -- Polar angle evolution along interface
      CASE 
        WHEN state = 'SLIDING' OR (SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 AND theta >= -1.57) THEN theta - 0.06
        ELSE theta
      END AS theta,
      -- State Transition
      CASE 
        WHEN theta <= -1.50 THEN 'DETACHED'
        WHEN SQRT((xp)*(xp) + (yp/0.85)*(yp/0.85)) <= 1.02 OR state = 'SLIDING' THEN 'SLIDING'
        ELSE 'APPROACHING'
      END AS state
    FROM particle_sim
    WHERE step < 75 AND yp > -3.5
  )
SELECT 
  bv.cell_id, bv.x, bv.y,
  CASE WHEN bv.r_eff <= 1.0 THEN 0.0 ELSE ROUND(bv.u_raw, 4) END AS u,
  CASE WHEN bv.r_eff <= 1.0 THEN 0.0 ELSE ROUND(bv.v_raw, 4) END AS v,
  ps.step, ps.xp, ps.yp, ps.up, ps.vp, ps.state
FROM buoyant_velocities bv
LEFT JOIN particle_sim ps ON bv.cell_id = ps.step + 1
ORDER BY bv.cell_id;
"""

# Run query in SQLite
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()
conn.close()

# 2. Extract Data
x_vals = sorted(list(set(row[1] for row in rows)))
y_vals = sorted(list(set(row[2] for row in rows)))

nx, ny = len(x_vals), len(y_vals)
X, Y = np.meshgrid(x_vals, y_vals)
U = np.zeros((ny, nx))
V = np.zeros((ny, nx))

particle_traj = []

for row in rows:
    cell_id, x, y, u, v, step, xp, yp, up, vp, state = row
    ix = x_vals.index(x)
    iy = y_vals.index(y)
    U[iy, ix] = u
    V[iy, ix] = v
    if xp is not None:
        particle_traj.append((xp, yp, state))

px = [pt[0] for pt in particle_traj]
py = [pt[1] for pt in particle_traj]

# Mask bubble interior
R_mesh = np.sqrt(X**2 + (Y / 0.85)**2)
U_masked = np.ma.masked_where(R_mesh <= 1.0, U)
V_masked = np.ma.masked_where(R_mesh <= 1.0, V)
Speed = np.sqrt(U_masked**2 + V_masked**2)

# 3. Plot Vector Field & Interface Sliding Path
fig, ax = plt.subplots(figsize=(8, 9))

# Speed Heatmap
c = ax.pcolormesh(X, Y, Speed, cmap='viridis', shading='auto', alpha=0.75)
fig.colorbar(c, ax=ax, label='Liquid Speed $\\sqrt{u^2 + v^2}$')

# Streamlines
ax.streamplot(x_vals, y_vals, U_masked, V_masked, color='white', density=1.1, linewidth=0.8)

# Draw Bubble Boundary Curve (Interface)
theta_arr = np.linspace(0, 2 * np.pi, 300)
bx = 1.0 * np.cos(theta_arr)
by = 0.85 * np.sin(theta_arr)
ax.plot(bx, by, color='#00838f', lw=3, zorder=5, label='Bubble-Water Interface ($r_{eff}=1.0$)')
ax.fill(bx, by, color='#e0f7fa', alpha=0.8, zorder=4)

# Plot Particle Trajectory directly along interface
ax.plot(px, py, color='red', linestyle='-', linewidth=3, zorder=8, label='Particle Path (Interface Sliding)')

# Key Points
ax.scatter([px[0]], [py[0]], color='yellow', edgecolors='black', s=110, zorder=10, label='Particle Approach')
ax.scatter([px[18]], [py[18]], color='orange', edgecolors='black', s=120, zorder=10, label='Interface Contact Point')
ax.scatter([px[-1]], [py[-1]], color='magenta', edgecolors='black', s=110, zorder=10, label='Detachment into Wake')

# Annotations
ax.annotate('Strict Sliding along Interface', xy=(px[28], py[28]), xytext=(px[28]+0.6, py[28]+0.2),
            arrowprops=dict(arrowstyle="->", color='red', lw=2), fontsize=10, fontweight='bold', color='darkred')

# Formatting
ax.set_title('Particle Hydrodynamics: Sliding Along Bubble-Water Interface', fontsize=11)
ax.set_xlabel('Horizontal Position $x$')
ax.set_ylabel('Vertical Position $y$')
ax.set_xlim(-3.0, 3.0)
ax.set_ylim(-4.0, 3.0)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.show()
