import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt

# Run source /opt/openfoam12/etc/bashrc
# Run foamToVTK

# Load the VTK file
mesh = pv.read("flotation_969.vtk")

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

# Debug: Show available arrays
print("Available arrays:", mesh.array_names)

# Choose the field (e.g., 'U.solid' or 'T.solid')
field_name = "U.solid"  # or use something else, e.g., "T.air", "alpha.water", etc.

# Check if field exists in point or cell data
if field_name in mesh.point_data:
    data = mesh.point_data[field_name]
elif field_name in mesh.cell_data:
    data = mesh.cell_data[field_name]
else:
    raise KeyError(f"Field {field_name} not found in point or cell data.")

# If it's a vector field (e.g., U.solid), calculate the magnitude
if data.ndim == 2:
    data = np.linalg.norm(data, axis=1)

# Coordinates (flatten to 1D arrays for contour plotting)
points = mesh.points
x = points[:, 0]
y = points[:, 1]

# Ensure lengths match (flatten if needed)
x = x.flatten()
y = y.flatten()
data = data.flatten()

# --- Create contour plot ---
plt.figure(figsize=(6,5))
plt.tricontourf(x, y, data, levels=50)
plt.colorbar(label=field_name)
plt.xlabel("x")
plt.ylabel("y")
plt.title(f"Contour plot of {field_name}")
plt.tight_layout()
plt.show()
