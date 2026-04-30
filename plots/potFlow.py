import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

# 1. Define the grid


x = np.linspace(-0.001, 0.001, 100)
y = np.linspace(-0.0015, 0.0015, 100)
X, Y = np.meshgrid(x, y)

# 2. Parameters
# U_inf: Free stream velocity
# R: Radius of the sphere
U_inf = 0.011
R = 0.00035

# 3. Calculate Stream Function (psi)
# For a sphere, we use spherical coordinates, but for a 2D cross-section:
# psi = U_inf * r^2 * sin^2(theta) * (1 - R^3/r^3) / 2
# In Cartesian (x,y) where r^2 = x^2 + y^2 and sin^2(theta) = y^2 / r^2:
r = np.sqrt(X**2 + Y**2)
# Prevent division by zero at the origin
r[r < R] = np.nan 

psi = 0.5 * U_inf * (X**2) * (1 - (R**3 / (r**3)))

# 4. Plotting
plt.figure(figsize=(8, 8))

# Draw the sphere (bubble)
circle = plt.Circle((0, 0), R, color='black', zorder=10)
plt.gca().add_patch(circle)

# Plot streamlines
plt.contour(X, Y, psi, levels=20, colors='blue', linewidths=1)

# Formatting
#plt.title('Streamlines around a Spherical Bubble (Potential Flow)')
plt.xlabel('Distance x')
plt.ylabel('Distance y')
plt.xlim(-0.001, 0.001)
plt.ylim(-0.0015, 0.0015)
plt.gca().set_aspect(1)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
