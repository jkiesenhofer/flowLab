import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Enable Matplotlib built-in LaTeX math engine
plt.rcParams['text.usetex'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

# 1. SQL Query calculating attachment efficiency vs contact angle
sql_query = """
WITH ANGLES AS (
    -- Generate contact angles theta from 1 to 60 degrees in steps of 0.5 degrees
    WITH RECURSIVE cnt(x) AS (
        SELECT 1.0
        UNION ALL
        SELECT x + 0.5 FROM cnt WHERE x < 60.0
    )
    SELECT x AS theta_deg FROM cnt
),
PARTICLE_SIZES AS (
    -- Fine particle sizes in meters and micrometers (10 um to 50 um)
    SELECT 10.0e-6 AS dp, 10 AS dp_um UNION ALL
    SELECT 20.0e-6 AS dp, 20 AS dp_um UNION ALL
    SELECT 30.0e-6 AS dp, 30 AS dp_um UNION ALL
    SELECT 40.0e-6 AS dp, 40 AS dp_um UNION ALL
    SELECT 50.0e-6 AS dp, 50 AS dp_um
),
CONSTANTS AS (
    -- Hydrodynamic parameters for a 0.3 mm micro-bubble
    SELECT 
        0.0003 AS db,      -- Bubble diameter: 0.3 mm (0.0003 m)
        0.030  AS u_b,     -- Micro-bubble rise velocity: ~0.03 m/s
        0.100  AS A_tau    -- Induction time proportionality constant (s*deg)
)
SELECT 
    a.theta_deg,
    p.dp_um,
    -- Calculate induction time tau_i = A_tau / theta (in seconds)
    (c.A_tau / a.theta_deg) AS tau_i,
    -- Dobby Attachment Efficiency Formula as a function of theta:
    -- E_a = sin^2( 2 * atan( exp( - (3 * u_b * (A_tau / theta)) / (db * (db/dp + 1)) ) ) ) * 100
    POWER(
        SIN(
            2.0 * ATAN(
                EXP(
                    - (3.0 * c.u_b * (c.A_tau / a.theta_deg)) / (c.db * (c.db / p.dp + 1.0))
                )
            )
        ), 
        2
    ) * 100.0 AS attachment_efficiency_percent
FROM ANGLES a
CROSS JOIN PARTICLE_SIZES p
CROSS JOIN CONSTANTS c
ORDER BY p.dp_um, a.theta_deg;
"""

# 2. Execute SQL query using SQLite in-memory engine
conn = sqlite3.connect(":memory:")
df = pd.read_sql_query(sql_query, conn)
conn.close()

# 3. Create Plot
plt.figure(figsize=(10, 6))

particle_sizes = df["dp_um"].unique()
colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"]

for dp, color in zip(particle_sizes, colors):
    subset = df[df["dp_um"] == dp]
    plt.plot(
        subset["theta_deg"], 
        subset["attachment_efficiency_percent"], 
        label=rf"$d_p = {dp}\;\mu\text{{m}}$", 
        color=color, 
        linewidth=2
    )

# Formatting Chart with LaTeX Math Syntax
plt.title(
    r"$\text{Dobby Model: } E_a(\theta) = \sin^2\left(2 \arctan \left[ \exp \left( -\frac{3 u_b \cdot \tau_i(\theta)}{d_b \left(\frac{d_b}{d_p} + 1\right)} \right) \right]\right) \quad (d_b = 0.3\text{ mm})$",
    fontsize=11, pad=12
)
plt.xlabel(r"$\text{Contact Angle } \theta \quad (^\circ)$", fontsize=11)
plt.ylabel(r"$\text{Attachment Efficiency } E_a \quad (\%) $", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.xlim(1, 60)
plt.ylim(-2, 105)
plt.legend(title=r"$\text{Particle Size } (d_p)$", frameon=True, fontsize=10)
plt.tight_layout()

# Save image directly to disk
output_file = "attachment_efficiency_vs_contact_angle_0.3mm.png"
plt.savefig(output_file, dpi=300)
print(f"Plot saved to '{output_file}' in your current working directory.")
