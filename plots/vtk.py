import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Run source /opt/openfoam12/etc/bashrc
# Run foamToVTK

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

# Load the VTK file
mesh = pv.read("flotation_805.vtk")

# Field to plot
field_name = "U.air"
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
x = mesh.points[:,0]#/max(mesh.points[:,0])
y = mesh.points[:,1]#/max(mesh.points[:,1])

# --- Create a regular grid for contour ---
xi = np.linspace(x.min(), x.max(), 300)
yi = np.linspace(y.min(), y.max(), 200)
X, Y = np.meshgrid(xi, yi)

# Interpolate scattered data onto grid
Z = griddata((x, y), data, (X, Y), method='linear')

# Plot using classic contour
plt.figure(figsize=(6,6))
contours = plt.contour(X, Y, Z, levels=7, colors="k")
plt.clabel(contours, inline=True, fontsize=8)
plt.xlabel("x")
plt.ylabel("y")
plt.title(f"Contour plot of {field_name}")
plt.axis('equal')          # ensures equal scaling on x and y
plt.tight_layout()
plt.show()
