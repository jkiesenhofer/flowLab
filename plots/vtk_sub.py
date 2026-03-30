import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Load the VTK file
mesh = pv.read("flotation_961.vtk")

# Enable LaTeX-style fonts
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

# Field to plot
field_name = "p"
if field_name in mesh.point_data:
    data = mesh.point_data[field_name]
elif field_name in mesh.cell_data:
    data = mesh.cell_data[field_name]
else:
    raise KeyError(f"Field {field_name} not found.")

# If vector, take magnitude
if data.ndim == 2:
    data = np.linalg.norm(data, axis=1)

# Coordinates
x = mesh.points[:, 0] / max(mesh.points[:, 0])
y = mesh.points[:, 1] / max(mesh.points[:, 1])

# --- Create a regular grid for contour ---
xi = np.linspace(x.min(), x.max(), 300)
yi = np.linspace(y.min(), y.max(), 200)
X, Y = np.meshgrid(xi, yi)

# Interpolate scattered data onto grid
Z = griddata((x, y), data, (X, Y), method='linear')

# Find the middle index of the grid
mid_index = int(len(Z[:, 1]) / 2)  # Middle row index

# Create subplots (1 row, 2 columns)
fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # 1x2 grid of subplots

# Set levels for contour plot
vmin, vmax = Z.min(), Z.max()
levels = np.linspace(vmin, vmax, 17)
levels = levels[1:]  # Exclude the first level (min)

# Plot the contour (first subplot)
contours = axs[0].contour(X, Y, Z, levels=levels, colors="k")
axs[0].clabel(contours, inline=True, fontsize=8)
axs[0].set_xlabel("x")
axs[0].set_ylabel("y")
axs[0].set_title(f"(a) {field_name}")
axs[0].axis('equal')  # Equal scaling on x and y

# Add a dashed line representing the middle plane (vertical line at X=0.5)
axs[0].axvline(x=0.5, color='r', linestyle='--', label='Middle Plane (x=0.5)')
axs[0].legend()

# Plot the values from the middle row (second subplot)
axs[1].plot(Z[:, mid_index], color="k")
axs[1].set_title(f"(b)")
axs[1].axis('equal')  # Equal scaling on x and y
axs[1].set_xlabel("Index")
axs[1].set_ylabel(f"{field_name}")

# Adjust layout to avoid overlap
plt.tight_layout()

# Show the plot
plt.show()
