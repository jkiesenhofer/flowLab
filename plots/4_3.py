import matplotlib.pyplot as plt
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

# Physical parameters (in millimeters)
bubble_size = 2.0  # Bubble characteristic length
particle_char_length = 0.8  # Particle characteristic length

# Define the radius of the underlying spherical particle (Radius = diameter / 2)
R = particle_char_length / 2.0  # Radius = 0.4 mm

# Create 3D figure
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(projection="3d")

# Longitude phi from 0 to 2*pi
phi = np.linspace(0, 2 * np.pi, 500)

# Define an arbitrary smooth closed path (contact line) on the sphere
theta_base = np.pi / 3
theta = (
    theta_base
    + 0.12 * np.sin(3 * phi)
    + 0.08 * np.cos(4 * phi)
    + 0.04 * np.sin(6 * phi)
)

# Convert spherical coordinates to Cartesian coordinates (dimensions in mm)
x = R * np.cos(theta) * np.cos(phi)
y = R * np.cos(theta) * np.sin(phi)
z = R * np.sin(theta)

# Plot only the arbitrary closed contact line path in black
ax.plot(
    x,
    y,
    z,
    color="black",
    linewidth=3.5,
    label="C",
)

# Force all axes to have the exact same length and range (symmetric padding around the sphere)
axis_limit = 0.5  # mm (slightly larger than R = 0.4 mm)
ax.set_xlim([-axis_limit, axis_limit])
ax.set_ylim([-axis_limit, axis_limit])
ax.set_zlim([-axis_limit, axis_limit])

# Ensure equal 3D box aspect ratio
ax.set_box_aspect([1, 1, 1])

ax.set_xlabel("X Axis (mm)")
ax.set_ylabel("Y Axis (mm)")
ax.set_zlabel("Z Axis (mm)")

plt.legend()
plt.show()
