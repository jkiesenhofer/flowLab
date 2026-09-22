import matplotlib.pyplot as plt
import numpy as np

# --- 1. Physical Parameters ---
diameter = 0.002  # Bubble diameter = 2 mm [m]
R = diameter / 2.0  # Bubble radius = 1 mm = 0.001 m [m]
nu = 1.0e-6  # Kinematic viscosity of water [m^2/s]

# Characteristic Reynolds numbers for the three regimes
Re_stokes = 0.1  # Stokes / Creeping flow (Re << 1)
Re_inter = 10.0  # Intermediate flow (Re ~ 10)
Re_potential = 200.0  # Potential / Inviscid flow (Re >> 1)


# --- 2. Flow Model Function (Vertical Flow Alignment) ---
def compute_vertical_bubble_flow(Re, R, nu, X, Y):
  # Calculate free-stream velocity based on target Reynolds number
  U_inf = (Re * nu) / diameter

  # Convert coordinates: theta is now measured from the vertical Y-axis
  r = np.sqrt(X**2 + Y**2)
  theta = np.arctan2(X, Y)  # Angle from positive Y-axis

  # Mask for points inside the bubble (r < R)
  mask = r < R

  if Re < 1.0:
    # Stokes / Creeping Flow (Vertical alignment)
    vr = U_inf * (1.0 - R / r) * np.cos(theta)
    vtheta = -U_inf * (1.0 - 0.5 * (R / r)) * np.sin(theta)
  elif Re > 100.0:
    # Potential Flow (Inviscid, vertical alignment)
    vr = U_inf * (1.0 - (R / r) ** 2) * np.cos(theta)
    vtheta = -U_inf * (1.0 + (R / r) ** 2) * np.sin(theta)
  else:
    # Intermediate Flow (Transition regime with vertical inertial distortion)
    vr = U_inf * (
        (1.0 - (R / r) ** 2) * np.cos(theta)
        + 0.15 * (1.0 - R / r) * np.cos(2 * theta)
    )
    vtheta = -U_inf * (1.0 + (R / r) ** 2) * np.sin(theta)

  # Transform polar velocities to Cartesian components (ux, uy) for vertical flow
  ux = vr * np.sin(theta) + vtheta * np.cos(theta)
  uy = vr * np.cos(theta) - vtheta * np.sin(theta)

  # Mask out values inside the bubble body
  ux[mask] = np.nan
  uy[mask] = np.nan

  return ux, uy, U_inf


# --- 3. Spatial Grid Setup ---
grid_extents = 3.5 * R
x = np.linspace(-grid_extents, grid_extents, 250)
y = np.linspace(-grid_extents, grid_extents, 250)
X, Y = np.meshgrid(x, y)

# Compute velocity fields for all 3 regimes with vertical flow
ux_s, uy_s, U_s = compute_vertical_bubble_flow(Re_stokes, R, nu, X, Y)
ux_i, uy_i, U_i = compute_vertical_bubble_flow(Re_inter, R, nu, X, Y)
ux_p, uy_p, U_p = compute_vertical_bubble_flow(Re_potential, R, nu, X, Y)

# --- 4. Plotting Results ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)

regimes = [
    (
        "Stokes Flow (Creeping)",
        Re_stokes,
        ux_s,
        uy_s,
        "Viscous Dominated\nFore-Aft Symmetric",
    ),
    (
        "Intermediate Flow",
        Re_inter,
        ux_i,
        uy_i,
        "Inertia & Viscosity Coexist\nTransition Phase",
    ),
    (
        "Potential Flow (Inviscid)",
        Re_potential,
        ux_p,
        uy_p,
        "Inertia Dominated\nFree-Slip Boundary",
    ),
]

for ax, (title, Re, ux, uy, desc) in zip(axes, regimes):
  # Compute speed for coloring streamlines
  speed = np.sqrt(ux**2 + uy**2)

  # Plot streamfield contours/lines
  strm = ax.streamplot(
      X * 1e3,
      Y * 1e3,
      ux,
      uy,
      color=speed,
      cmap="YlGnBu",
      linewidth=1.3,
      density=1.6,
  )

  # Draw the 2 mm bubble (Radius = 1 mm) at the center
  bubble = plt.Circle(
      (0, 0),
      R * 1e3,
      color="orange",
      ec="black",
      linewidth=1.5,
      zorder=5,
      label="2mm Bubble",
  )
  ax.add_patch(bubble)

  ax.set_title(
      f"{title}\n$Re = {Re}$ | $U_\infty = {U_s*1000:.1f}$ mm/s", fontsize=11
  )
  ax.set_xlabel("X position [mm]")
  ax.set_ylabel("Y position [mm]")
  ax.set_aspect("equal")
  ax.grid(True, linestyle=":", alpha=0.6)

axes[0].set_ylabel("Y position [mm]")
plt.suptitle(
    "Vertical Hydrodynamic Flow Regimes Around a 2 mm Air Bubble ($R = 1$ mm)",
    fontsize=15,
    fontweight="bold",
    y=1.03,
)
plt.tight_layout()
plt.show()
