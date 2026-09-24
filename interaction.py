import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# 1. Execute SQL Query via SQLite for Fluid Mesh + Particle Trajectory Dynamics
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
  -- Flow Parameters: U_rise = 1.0, R = 1.0 (ellipsoidal b=0.85)
  params AS (
    SELECT 1.0 AS U_rise, 1.0 AS R
  ),
  buoyant_calc AS (
    SELECT 
      ROW_NUMBER() OVER (ORDER BY x.ix, y.iy) AS cell_id,
      x.x,
      y.y,
      p.U_rise,
      p.R,
      ROUND(SQRT(x.x * x.x + (y.y / 0.85) * (y.y / 0.85)), 4) AS r_eff,
      ROUND(SQRT(x.x * x.x + y.y * y.y), 4) AS r
    FROM x_steps x
    CROSS JOIN y_steps y
    CROSS JOIN params p
  ),
  buoyant_velocities AS (
    SELECT 
      cell_id,
      x,
      y,
      r_eff,
      r,
      CASE 
        WHEN r_eff <= R THEN 0.0
        WHEN y < -R THEN -0.8 * U_rise * (x / (R + ABS(y))) * EXP(-(x * x + (y + 1.5) * (y + 1.5)))
        ELSE -U_rise * (1.5 * (R * R) / (r * r)) * (x * y / (r * r))
      END AS u_raw,
      CASE 
        WHEN r_eff <= R THEN 0.0
        WHEN y < -R THEN -U_rise + 0.6 * U_rise * EXP(-(x * x) / (0.8 * R)) * EXP(0.4 * y)
        ELSE -U_rise * (1.0 - 0.5 * (R / r) + 1.5 * (R * R * y * y) / (r * r * r * r))
      END AS v_raw
    FROM buoyant_calc
  ),
  -- Particle Trajectory Simulation via Recursive CTE (Approaching from y = 2.5)
  particle_sim AS (
    -- Initial State: t=0, particle at x_p = 0.35, y_p = 2.5
    SELECT 
      0 AS step,
      0.0 AS t,
      0.35 AS xp,
      2.5 AS yp,
      0.0 AS up,
      -0.8 AS vp,
      'APPROACHING' AS state
    UNION ALL
    SELECT 
      step + 1,
      ROUND((step + 1) * 0.05, 3) AS t,
      -- Position update
      ROUND(
        CASE 
          -- Contact phase: Sliding around bubble interface (R_eff ~ 1.05)
          WHEN SQRT(xp*xp + (yp/0.85)*(yp/0.85)) <= 1.05 THEN
            1.05 * COS(ATAN2(yp/0.85, xp))
          ELSE xp + up * 0.05 
        END, 4
      ) AS xp,
      ROUND(
        CASE 
          WHEN SQRT(xp*xp + (yp/0.85)*(yp/0.85)) <= 1.05 THEN
            1.05 * 0.85 * SIN(ATAN2(yp/0.85, xp))
          ELSE yp + vp * 0.05 
        END, 4
      ) AS yp,
      -- Velocity update (Stokes drag driving towards fluid velocity + sliding force)
      ROUND(
        CASE 
          WHEN SQRT(xp*xp + (yp/0.85)*(yp/0.85)) <= 1.05 THEN 0.6 * (xp / SQRT(xp*xp + yp*yp))
          ELSE up + 4.0 * ((-1.0 * (1.5 / (xp*xp + yp*yp)) * (xp * yp / (xp*xp + yp*yp))) - up) * 0.05
        END, 4
      ) AS up,
      ROUND(
        CASE 
          WHEN SQRT(xp*xp + (yp/0.85)*(yp/0.85)) <= 1.05 THEN -0.8 * ABS(yp / SQRT(xp*xp + yp*yp))
          ELSE vp + 4.0 * ((-1.0 * (1.0 - 0.5 / SQRT(xp*xp + yp*yp))) - vp) * 0.05 - 0.2 * 0.05
        END, 4
      ) AS vp,
      CASE 
        WHEN SQRT(xp*xp + (yp/0.85)*(yp/0.85)) <= 1.06 AND yp > -0.2 THEN 'SURFACE CONTACT / SLIDING'
        WHEN yp <= -0.2 THEN 'DETACHED IN WAKE'
        ELSE 'APPROACHING'
      END AS state
    FROM particle_sim
    WHERE step < 70 AND yp > -3.5
  )
-- Return fluid grid rows along with particle positions
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

# 2. Extract Fluid Field and Particle Trajectory
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
        particle_traj.append((xp, yp, up, vp, state))

px = [pt[0] for pt in particle_traj]
py = [pt[1] for pt in particle_traj]

# Mask interior of bubble
R_mesh = np.sqrt(X**2 + (Y / 0.85)**2)
U_masked = np.ma.masked_where(R_mesh <= 1.0, U)
V_masked = np.ma.masked_where(R_mesh <= 1.0, V)
Speed = np.sqrt(U_masked**2 + V_masked**2)

# 3. Plot Fluid Field + Particle Contact Trajectory
fig, ax = plt.subplots(figsize=(8, 9))

# Background fluid speed heatmap
c = ax.pcolormesh(X, Y, Speed, cmap='viridis', shading='auto', alpha=0.75)
fig.colorbar(c, ax=ax, label='Liquid Speed $\\sqrt{u^2 + v^2}$')

# Streamlines of fluid
ax.streamplot(x_vals, y_vals, U_masked, V_masked, color='white', density=1.1, linewidth=0.8)

# Bubble boundary
theta = np.linspace(0, 2 * np.pi, 200)
bx = 1.0 * np.cos(theta)
by = 0.85 * np.sin(theta)
ax.fill(bx, by, color='#e0f7fa', ec='#00838f', lw=2.5, zorder=5, label='Buoyant Bubble ($R=1$)')

# Plot Particle Trajectory
ax.plot(px, py, color='red', linestyle='--', linewidth=2.5, zorder=8, label='Particle Trajectory')

# Draw particle at key positions (Approach, Contact, Detachment)
ax.scatter([px[0]], [py[0]], color='yellow', edgecolors='black', s=120, zorder=10, label='Particle Start')
ax.scatter([px[18]], [py[18]], color='orange', edgecolors='black', s=130, zorder=10, label='First Contact Point')
ax.scatter([px[-1]], [py[-1]], color='magenta', edgecolors='black', s=120, zorder=10, label='Detached in Wake')

# Trajectory Annotation Arrows
ax.annotate('1. Approaching', xy=(px[5], py[5]), xytext=(px[5]+0.6, py[5]+0.3),
            arrowprops=dict(arrowstyle="->", color='red', lw=1.5), fontsize=10, fontweight='bold', color='darkred')
ax.annotate('2. Contact & Sliding', xy=(px[20], py[20]), xytext=(px[20]+0.8, py[20]),
            arrowprops=dict(arrowstyle="->", color='orange', lw=1.5), fontsize=10, fontweight='bold', color='darkorange')
ax.annotate('3. Wake Detachment', xy=(px[-10], py[-10]), xytext=(px[-10]+0.6, py[-10]-0.3),
            arrowprops=dict(arrowstyle="->", color='magenta', lw=1.5), fontsize=10, fontweight='bold', color='purple')

# Formatting
ax.set_title('Approaching Particle Hydrodynamics & Surface Contact with Rising Bubble', fontsize=11)
ax.set_xlabel('Horizontal Position $x$')
ax.set_ylabel('Vertical Position $y$')
ax.set_xlim(-3.0, 3.0)
ax.set_ylim(-4.0, 3.0)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.show()
