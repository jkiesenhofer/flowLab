import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

# 1. Define parameter ranges
contact_angle = np.linspace(
    10, 170, 50
)  # Contact angle (theta in degrees)
re_number = np.linspace(0.1, 100, 50)  # Bubble Reynolds number (Re)

# Create a 2D grid for the surface plot
Theta, Re = np.meshgrid(contact_angle, re_number)

# 2. Define a representative model for Three-phase Contact Line Length (L, in micrometers)
# Note: Replace this synthetic relation with your actual experimental or numerical data function.
L0 = 50.0  # Base characteristic length scale
L = L0 * (Re**0.25) * np.sin(np.radians(Theta)) ** 0.5

# 3. Initialize the 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_layout(projection='3d') if hasattr(fig, 'add_layout') else fig.add_subplot(projection='3d')

# Plot the surface
surf = ax.plot_surface(
    Theta, Re, L, 
    cmap=cm.plasma, 
    edgecolor='none', 
    alpha=0.8, 
    antialiased=True,
    shade=True
)

# 4. Format axes and labels
ax.set_xlabel('Contact Angle (degrees)', labelpad=10)
ax.set_ylabel('Bubble Reynolds Number', labelpad=10)
ax.set_zlabel('Contact Line Length (um)', labelpad=10)


# Add a color bar for depth reference
fig.colorbar(surf, shrink=0.5, aspect=8, label='Contact Line Length (um)')

# Adjust view angle for optimal visibility
ax.view_init(elev=30, azim=135)

plt.tight_layout()
plt.show()
