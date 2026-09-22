import os
import urllib.request
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

DB_FILE = "flotation_simulation.db"
URL = "http://jkiesenhofer.bplaced.net/db/flotation_simulation.db"

# 1. Download database if not present
if not os.path.exists(DB_FILE):
    print(f"Downloading database from {URL}...")
    urllib.request.urlretrieve(URL, DB_FILE)
    print("Download complete.")
else:
    print(f"Database file '{DB_FILE}' already exists locally.")

# 2. Connect and load simulation data
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM simulation_data", conn)
conn.close()

# 3. Select 5 evenly spaced frames from the dataset
all_frames = sorted(df['frame'].unique())
if len(all_frames) >= 5:
    indices = np.linspace(0, len(all_frames) - 1, 5, dtype=int)
    selected_frames = [all_frames[i] for i in indices]
else:
    selected_frames = all_frames

print(f"Selected frames for comparison: {selected_frames}")

# Kinematic viscosity of water at ~20°C (m²/s)
NU_WATER = 1e-6 

# 4. Set up the single plot for all 5 frames
plt.figure(figsize=(12, 7))

for frame in selected_frames:
    df_filtered = df[df['frame'] == frame]
    if len(df_filtered) < 10:
        continue
        
    # Extract coordinates and convert from mm to meters
    x = (df_filtered['x_mm'] / 1000.0).values
    z = (df_filtered['z_mm'] / 1000.0).values
    vx = df_filtered['vx'].values
    vz = df_filtered['vz'].values

    # Create a regular 2D grid in X-Z space (in meters)
    grid_resolution = 60
    xi = np.linspace(x.min(), x.max(), grid_resolution)
    zi = np.linspace(z.min(), z.max(), grid_resolution)
    XI, ZI = np.meshgrid(xi, zi)

    # Interpolate scatter velocities onto the regular grid
    VXI = griddata((x, z), vx, (XI, ZI), method='linear', fill_value=0)
    VZI = griddata((x, z), vz, (XI, ZI), method='linear', fill_value=0)

    # Compute spatial gradients (in 1/s)
    d_vxi_dx, d_vxi_dz = np.gradient(VXI, xi, zi)
    d_vzi_dx, d_vzi_dz = np.gradient(VZI, xi, zi)
    
    # Compute Turbulent Dissipation Rate (epsilon = nu * sum(gradients^2)) in m²/s³
    dissipation_rate = NU_WATER * (d_vxi_dx**2 + d_vxi_dz**2 + d_vzi_dx**2 + d_vzi_dz**2)

    # Compute average dissipation rate as a function of height
    avg_dissipation_z = np.mean(dissipation_rate, axis=1)
    zi_mm = zi * 1000.0  # Convert height back to mm for plotting

    # Plot line for this specific frame
    plt.plot(zi_mm, avg_dissipation_z, linewidth=2, marker='o', markersize=3, label=f"Frame {frame}")

# 5. Finalize plot layout with Y-axis limit set to 0.075
plt.xlabel("Height Z [mm]", fontsize=12)
plt.ylabel(r"Dissipation Rate $\epsilon$ [$m^2/s^3$]", fontsize=12)
plt.ylim(0, 0.075)
plt.legend(title="Simulation Frames")
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()
