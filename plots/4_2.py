import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


# Define physical parameters (example values)
Rp = 50.0  # Particle radius (e.g., micrometers)
gamma_LG = 0.0728  # Liquid-gas surface tension (e.g., N/m for water)

# Define ranges for the two variables (in degrees)
theta_tpc_deg = np.linspace(5, 175, 150)
theta_ar_deg = np.linspace(-90, 90, 150)

# Create a 2D meshgrid
Theta_TPC, Theta_AR = np.meshgrid(theta_tpc_deg, theta_ar_deg)

# Convert degrees to radians for trigonometric calculations
theta_tpc_rad = np.radians(Theta_TPC)
theta_ar_rad = np.radians(Theta_AR)

# Calculate F_TPC,z according to the formula:
F_z = (
    2
    * np.pi
    * Rp
    * gamma_LG
    * np.sin(theta_tpc_rad)
    * np.sin(theta_tpc_rad + theta_ar_rad)
)

# Set up the 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot the surface
surf = ax.plot_surface(
    Theta_TPC, Theta_AR, F_z, cmap="viridis", edgecolor="none", alpha=0.9
)

# Axis labels and formatting with fixed LaTeX syntax

ax.set_xlabel(r"$\theta_{\text{TPC}}$ (°)", fontsize=11, labelpad=10)
# Fixed slash and text block definition:
ax.set_ylabel(r"$\theta_{\text{A}/\text{R}}$ (°)", fontsize=11, labelpad=10)

# Add a color bar mapping force values
fig.colorbar(surf, shrink=0.5, aspect=10, label=r"$F_{\text{TPC}}$")

# Adjust viewing angle for better perspective
ax.view_init(elev=30, azim=135)

plt.tight_layout()
plt.show()
