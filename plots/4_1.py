import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.titlesize": 14
})

# 1. Define parameter ranges
contact_angle = np.linspace(10, 170, 40)  # Contact angle (theta in degrees)
re_number = np.linspace(0.1, 100, 40)     # Bubble Reynolds number (Re)
ca_values = [0.001, 0.01, 0.1]           # Different Capillary numbers (Ca)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c'] # Distinct colors for each Ca

# Create a 2D grid for the surface plots
Theta, Re = np.meshgrid(contact_angle, re_number)

# 2. Initialize a single 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(projection='3d')
L0 = 50.0  # Base characteristic length scale

legend_elements = []

for ca, color in zip(ca_values, colors):
    # Representative model incorporating Capillary number (Ca) and Reynolds number (Re)
    L = L0 * (Re**0.25) * (ca**0.15) * np.sin(np.radians(Theta)) ** 0.5
    
    # Plot the surface with semi-transparency to see intersections clearly
    surf = ax.plot_surface(
        Theta, Re, L, 
        color=color, 
        edgecolor='none', 
        alpha=0.6, 
        antialiased=True,
        shade=True
    )
    
    # Create proxy artist for the legend
    legend_elements.append(Line2D([0], [0], color=color, lw=4, label=f'$Ca = {ca}$'))

# 3. Format axes, titles, and labels

ax.set_xlabel(r'Contact Angle ($^\circ$)', labelpad=10)
ax.set_ylabel('Reynolds Number ($Re$)', labelpad=10)
ax.set_zlabel('Contact Line Length ($\mu$m)', labelpad=10)

# Add the legend to the plot
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.95))

# Adjust view angle for optimal visibility
ax.view_init(elev=30, azim=135)

plt.tight_layout()
plt.show()
