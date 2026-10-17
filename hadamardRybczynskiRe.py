import numpy as np
import matplotlib.pyplot as plt

# --- 1. Parameters & Constants ---
d_bubble = 0.002       # Bubble diameter = 2 mm (0.002 m)
a = d_bubble / 2.0     # Bubble radius = 1 mm (0.001 m)
rho = 1000.0           # Density of ambient fluid (water) [kg/m^3]
mu = 0.001             # Dynamic viscosity of ambient fluid [Pa·s]
nu = mu / rho          # Kinematic viscosity [m^2/s]
g = 9.81               # Gravitational acceleration [m/s^2]

# Hadamard-Rybczynski terminal velocity for a gas bubble
U = (1.0 / 3.0) * (a**2 * g * rho) / mu
print(f"Calculated Terminal Velocity (U): {U:.4f} m/s")

# Global Reynolds number based on terminal velocity
Re_global = (U * d_bubble) / nu
print(f"Global Reynolds Number (Re): {Re_global:.2f}")

# --- 2. Grid Setup ---
n_points = 400
x = np.linspace(-3 * a, 3 * a, n_points)
z = np.linspace(-3 * a, 3 * a, n_points)
X, Z = np.meshgrid(x, z)
R = np.sqrt(X**2 + Z**2)

# --- 3. Hadamard-Rybczynski Stream Function ($\psi$) ---
Psi = np.zeros_like(R)
inner_mask = R < a
Psi[inner_mask] = (U * X[inner_mask]**2 / 4.0) * (1.0 - (R[inner_mask]**2 / a**2))
outer_mask = ~inner_mask
Psi[outer_mask] = -0.5 * U * X[outer_mask]**2 * (1.0 - a / R[outer_mask])

# --- 4. Velocity Field & Local Reynolds Number Field Calculation ---
dx = x[1] - x[0]
dz = z[1] - z[0]
dPsi_dz, dPsi_dx = np.gradient(Psi, dz, dx)
u_x = -dPsi_dz
u_z = dPsi_dx
U_mag = np.sqrt(u_x**2 + u_z**2)

# Compute the local Reynolds number field: Re(x,z) = (U_mag * d_bubble) / nu
Re_field = (U_mag * d_bubble) / nu

# --- 5. Visualization (Local Reynolds Number Field) ---
fig, ax = plt.subplots(figsize=(8, 8))

# Contour plot of the local Reynolds number field
contour_levels = np.linspace(Re_field.min(), Re_field.max(), 30)
cf = ax.contourf(X * 1e3, Z * 1e3, Re_field, levels=contour_levels, cmap='viridis', alpha=0.9)
cbar = fig.colorbar(cf, ax=ax)
cbar.set_label('Local Reynolds Number Field $Re(x,z)$', fontsize=10)

# Overlay streamlines in white for contrast against the viridis colormap
ax.streamplot(X * 1e3, Z * 1e3, u_x, u_z, color='white', linewidth=0.8, density=1.5, arrowstyle='->')

# Draw the bubble boundary circle (r = a)
bubble_boundary = plt.Circle((0, 0), a * 1e3, color='red', fill=False, linestyle='--', linewidth=2, label='Bubble Interface ($r = a$)')
ax.add_patch(bubble_boundary)

# Plot formatting
ax.set_aspect('equal')
ax.set_title(f'Local Reynolds Number Field Around a 2 mm Gas Bubble\n(Global $Re$ = {Re_global:.1f})', fontsize=12)
ax.set_xlabel('Horizontal Coordinate $x$ [mm]', fontsize=10)
ax.set_ylabel('Vertical Coordinate $z$ [mm]', fontsize=10)
ax.set_xlim(-3 * a * 1e3, 3 * a * 1e3)
ax.set_ylim(-3 * a * 1e3, 3 * a * 1e3)
ax.legend(loc='upper right')
ax.grid(True, linestyle=':', alpha=0.3)

plt.tight_layout()
plt.show()
