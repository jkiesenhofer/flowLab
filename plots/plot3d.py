import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
})

df = pd.read_csv("OF/flotation_10/data2.csv")

x = df["U.air_Magnitude"].values
y = df["U.solid_Magnitude"].values
z = df["U.water_Magnitude"].values

# Create interpolation grid
grid_x, grid_y = np.mgrid[
    x.min():x.max():100j,
    y.min():y.max():100j
]

# Interpolate
grid_z = griddata((x, y), z, (grid_x, grid_y), method="cubic")

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# surface plot from interpolated data
surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap="viridis", alpha=0.8)

# original points
ax.scatter(x, y, z, color="black", s=5)

ax.set_xlabel(r"$U_{air}$")
ax.set_ylabel(r"$U_{solid}$")
ax.set_zlabel(r"$U_{water}$")

# fig.colorbar(surf, ax=ax)

plt.show()
