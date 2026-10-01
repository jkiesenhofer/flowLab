import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Enable Matplotlib built-in LaTeX math engine
plt.rcParams['text.usetex'] = False
plt.rcParams['mathtext.fontset'] = 'cm'

# 1. SQL Query calculating Collision Efficiency vs Bubble Reynolds Number
sql_query = """
WITH RECURSIVE REYNOLDS_NUMBERS(Re_b) AS (
    -- Discrete evaluation points (0 to 500)
    SELECT 0.0
    UNION ALL SELECT 15.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 0.0
    UNION ALL SELECT 30.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 15.0
    UNION ALL SELECT 50.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 30.0
    UNION ALL SELECT 75.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 50.0
    UNION ALL SELECT 100.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 75.0
    UNION ALL SELECT 130.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 100.0
    UNION ALL SELECT 160.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 130.0
    UNION ALL SELECT 200.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 160.0
    UNION ALL SELECT 250.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 200.0
    UNION ALL SELECT 300.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 250.0
    UNION ALL SELECT 350.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 300.0
    UNION ALL SELECT 400.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 350.0
    UNION ALL SELECT 450.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 400.0
    UNION ALL SELECT 500.0 FROM REYNOLDS_NUMBERS WHERE Re_b = 450.0
),
PARTICLE_SIZES AS (
    -- Particle diameters in micrometers (20 um to 100 um)
    SELECT 20 AS dp_um UNION ALL
    SELECT 40 AS dp_um UNION ALL
    SELECT 60 AS dp_um UNION ALL
    SELECT 80 AS dp_um UNION ALL
    SELECT 100 AS dp_um
),
PARAMETERS AS (
    -- Bubble diameter fixed at 0.5 mm = 500 um
    SELECT 500.0 AS db_um
)
SELECT 
    r.Re_b,
    p.dp_um,
    -- Collision Efficiency formula in SQL (expressed as percentage)
    CASE 
        WHEN r.Re_b = 0 THEN 0.0
        ELSE 100.0 * POWER(CAST(p.dp_um AS FLOAT) / param.db_um, 2) * (
            1.5 + (0.15 * POWER(r.Re_b, 0.72)) / (1.0 + 0.015 * POWER(r.Re_b, 0.27))
        )
    END AS collision_efficiency_percent
FROM REYNOLDS_NUMBERS r
CROSS JOIN PARTICLE_SIZES p
CROSS JOIN PARAMETERS param
ORDER BY p.dp_um, r.Re_b;
"""

# 2. Execute SQL query using SQLite in-memory engine
conn = sqlite3.connect(":memory:")
df = pd.read_sql_query(sql_query, conn)
conn.close()

# 3. Create Plot matching the template style
plt.figure(figsize=(10, 6))

particle_sizes = sorted(df["dp_um"].unique())
colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]

for dp, color in zip(particle_sizes, colors):
    subset = df[df["dp_um"] == dp]
    plt.plot(
        subset["Re_b"], 
        subset["collision_efficiency_percent"], 
        label=rf"$d_p = {dp}\;\mu\text{{m}}$", 
        color=color, 
        linewidth=2
    )

# Formatting Chart with LaTeX Math Syntax
plt.title(
    r"$\text{Collision Efficiency: } E_c(\text{Re}_b) = \left(\frac{d_p}{d_b}\right)^2 \left[\frac{3}{2} + \frac{0.15\,\text{Re}_b^{0.72}}{1 + 0.015\,\text{Re}_b^{0.27}}\right] \quad (d_b = 0.5\text{ mm})$",
    fontsize=11, pad=12
)
plt.xlabel(r"$\text{Bubble Reynolds Number } \text{Re}_b$", fontsize=11)
plt.ylabel(r"$\text{Collision Efficiency } E_c \quad (\%) $", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.xlim(0, 500)
plt.ylim(bottom=0)
plt.legend(title=r"$\text{Particle Size } (d_p)$", frameon=True, fontsize=10)
plt.tight_layout()

# Save image directly to disk
output_file = "collision_efficiency_vs_reynolds_number.png"
plt.savefig(output_file, dpi=300)
print(f"Plot saved to '{output_file}' in your current working directory.")
