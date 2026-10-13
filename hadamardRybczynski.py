import numpy as np
import matplotlib.pyplot as plt

# --- 1. Parameters & Constants ---
d_bubble = 0.002       # Bubble diameter = 2 mm (0.002 m)
a = d_bubble / 2.0     # Bubble radius = 1 mm (0.001 m)
rho = 1000.0           # Density of ambient fluid (water) [kg/m^3]
mu = 0.001             # Dynamic viscosity of ambient fluid [Pa·s]
g = 9.81               # Gravitational acceleration [m/s^2]

# Hadamard-Rybczynski terminal velocity for a gas bubble (viscosity ratio kappa -> 0)
# U = (1/3) * (a^2 * g * rho) / mu
U = (1.0 / 3.0) * (a**2 * g * rho) / mu
print(f"Calculated Terminal Velocity (U): {U:.4f} m/s")

# --- 2. Grid Setup ---
# Create a 2D spatial grid (x: horizontal, z: vertical) from -3a to 3a
n_points = 400
x = np.linspace(-3 * a, 3 * a, n_points)
z = np.linspace(-3 * a, 3 * a, n_points)
X, Z = np.meshgrid(x, z)
R = np.sqrt(X**2 + Z**2)

# --- 3. Hadamard-Rybczynski Stream Function ($\psi$) ---
# Initialize stream function array
Psi = np.zeros_like(R)

# Inside the bubble (r < a)
inner_mask = R < a
Psi[inner_mask] = (U * X[inner_mask]**2 / 4.0) * (1.0 - (R[inner_mask]**2 / a**2))

# Outside the bubble (r >= a) - accounts for interfacial slip velocity
outer_mask = ~inner_mask
Psi[outer_mask] = -0.5 * U * X[outer_mask]**2 * (1.0 - a / R[outer_mask])

# --- 4. Velocity Field Calculation via Numerical Gradient ---
# In 2D cylindrical/axisymmetric coordinates mapped to Cartesian (x, z):
# u_x = - d(Psi)/dz, u_z = d(Psi)/dx
dx = x[1] - x[0]
dz = z[1] - z[0]
dPsi_dz, dPsi_dx = np.gradient(Psi, dz, dx)
u_x = -dPsi_dz
u_z = dPsi_dx
U_mag = np.sqrt(u_x**2 + u_z**2)

# --- 5. Visualization (2D Contour & Streamlines) ---
fig, ax = plt.subplots(figsize=(8, 8))

# Contour plot of the stream function
contour_levels = np.linspace(Psi.min(), Psi.max(), 30)
cf = ax.contourf(X * 1e3, Z * 1e3, Psi, levels=contour_levels, cmap='coolwarm', alpha=0.8)
cbar = fig.colorbar(cf, ax=ax)
cbar.set_label('Stream Function $\\psi$ [$m^3/s$]')

# Overlay streamlines to visualize internal circulation and slip flow past the bubble
ax.streamplot(X * 1e3, Z * 1e3, u_x, u_z, color='k', linewidth=0.8, density=1.5, arrowstyle='->')

# Draw the bubble boundary circle (r = a)
bubble_boundary = plt.Circle((0, 0), a * 1e3, color='black', fill=False, linestyle='--', linewidth=2, label='Bubble Interface ($r = a$)')
ax.add_patch(bubble_boundary)

# Plot formatting
ax.set_aspect('equal')
ax.set_title(f'Hadamard-Rybczynski Flow Around a 2 mm Gas Bubble\n(Slip Velocity Enabled, $U$ = {U:.3f} m/s)', fontsize=12)
ax.set_xlabel('Horizontal Coordinate $x$ [mm]', fontsize=10)
ax.set_ylabel('Vertical Coordinate $z$ [mm]', fontsize=10)
ax.set_xlim(-3 * a * 1e3, 3 * a * 1e3)
ax.set_ylim(-3 * a * 1e3, 3 * a * 1e3)
ax.legend(loc='upper right')
ax.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()
