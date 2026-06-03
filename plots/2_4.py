import os
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 26
})

# 1. List your three specific VTK file names here
file_names = [
    "flotation9_3248.vtk",
    "flotation9_5371.vtk",  # Replace with your actual second filename
    "flotation9_7726.vtk",  # Replace with your actual third filename
]

field_name = "alpha.map"

# 2. Setup the horizontal subplot (1 row, 3 columns)
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

chosen_cmap = "YlGnBu"
min_cutoff = 0
max_cutoff = 2
levels = np.linspace(min_cutoff, max_cutoff, 100)

contour_filled = None

# 3. Loop through files and axes simultaneously
for i, (file_name, ax) in enumerate(zip(file_names, axes)):

    # Safety check: Skip processing if a file is missing
    if not os.path.exists(file_name):
        ax.text(
            0.5,
            0.5,
            f"File Not Found:\n{file_name}",
            ha="center",
            va="center",
            color="red",
        )
        ax.set_title(f"Slot {i+1} (Missing)", fontsize=12, color="red")
        continue

    print(f"Processing plot {i+1}/3: {file_name}...")

    # Load and process the current VTK file
    mesh = pv.read(file_name)

    if field_name in mesh.cell_data:
        mesh = mesh.cell_data_to_point_data()

    x = mesh.points[:, 0]
    y = mesh.points[:, 1]
    capillary_number = mesh.point_data[field_name]

    # Plot the unique file data on the current axis 'ax'
    contour_filled = ax.tricontourf(
        x,
        y,
        capillary_number,
        levels=levels,
        cmap=chosen_cmap,
        extend="both",
        antialiased=True,
    )

    # Individual subplot formatting
    ax.set_aspect("equal")
    ax.set_xlabel("X Coordinate", fontsize=10)
    if i == 0:
        ax.set_ylabel("Y Coordinate", fontsize=10)  # Only show Y label on the first plot

    # Title each subplot with its specific filename
    #ax.set_title(file_name, fontsize=11, fontweight="bold")

# 4. Add the unified colorbar legend if at least one file loaded successfully
if contour_filled is not None:
    cbar = fig.colorbar(
        contour_filled, ax=axes.ravel().tolist(), shrink=0.75, pad=0.03
    )
    cbar.set_label("Alpha Map", fontsize=12, labelpad=10)

# Main overall figure title
#fig.suptitle(
#    "Capillary Number Distribution Across Timesteps",
#    fontsize=15,
#    fontweight="bold",
#    y=0.98,
#)

plt.show()
