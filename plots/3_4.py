import numpy as np
import matplotlib.pyplot as plt

# Enable Matplotlib LaTeX rendering engine
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "text.latex.preamble": r"\usepackage{amsmath}"
})

def top_to_bottom_stokes_flow_2d(x, y, a=1.0, U=1.0):
    """
    Computes 2D Stokes flow velocity around a circular bubble of radius 'a'
    with far-field flow moving VERTICALLY DOWNWARD (top to bottom along -y).
    """
    r = np.sqrt(x**2 + y**2)
    
    if np.any(r < a):
        r = np.maximum(r, a + 1e-6)
        
    theta_d = np.arctan2(x, -y)
    
    # Velocity field components in polar coordinates
    u_r = U * np.cos(theta_d) * (1.0 - a / r)
    u_theta = -U * np.sin(theta_d) * (1.0 - a / (2.0 * r))
    
    # Transform back to Cartesian coordinates (ux, uy)
    ux = u_r * np.sin(theta_d) + u_theta * np.cos(theta_d)
    uy = -(u_r * np.cos(theta_d) - u_theta * np.sin(theta_d))
    
    return ux, uy

def simulate_downward_trajectory(
    a=1.0, 
    U=1.0, 
    D=0.012, 
    x0=0.2, 
    y0=3.8, 
    dt=0.005, 
    n_steps=2000, 
    seed=None
):
    """
    Simulates Langevin trajectory in downward Stokes flow (top to bottom).
    """
    if seed is not None:
        np.random.seed(seed)
        
    x = np.zeros(n_steps)
    y = np.zeros(n_steps)
    
    x[0], y[0] = x0, y0
    
    for i in range(1, n_steps):
        curr_x, curr_y = x[i-1], y[i-1]
        
        # Collision with bubble surface (r <= a)
        if np.hypot(curr_x, curr_y) <= a:
            x[i:] = curr_x
            y[i:] = curr_y
            break
            
        ux, uy = top_to_bottom_stokes_flow_2d(curr_x, curr_y, a=a, U=U)
        
        # 2D Gaussian white noise (Brownian motion)
        xi_x, xi_y = np.random.normal(0, 1, 2)
        
        # Langevin integration step
        x[i] = curr_x + ux * dt + np.sqrt(2 * D * dt) * xi_x
        y[i] = curr_y + uy * dt + np.sqrt(2 * D * dt) * xi_y
        
    return x, y

# --- Simulation & Plotting Parameters ---
bubble_radius = 1.0
far_field_velocity = 1.0
diffusion_coeff = 0.012
num_particles = 6

fig, ax = plt.subplots(figsize=(7, 9), dpi=150)

# 1. Background Streamlines (Top-to-Bottom Flow)
grid_x, grid_y = np.meshgrid(np.linspace(-3, 3, 150), np.linspace(-4, 4, 150))
Ux, Uy = np.zeros_like(grid_x), np.zeros_like(grid_y)

for i in range(grid_x.shape[0]):
    for j in range(grid_x.shape[1]):
        r_val = np.hypot(grid_x[i, j], grid_y[i, j])
        if r_val > bubble_radius:
            Ux[i, j], Uy[i, j] = top_to_bottom_stokes_flow_2d(
                grid_x[i, j], grid_y[i, j], a=bubble_radius, U=far_field_velocity
            )

ax.streamplot(grid_x, grid_y, Ux, Uy, color='lightgray', density=1.2, linewidth=0.8, arrowsize=0.8)

# 2. Central Bubble Circle
bubble = plt.Circle(
    (0, 0), bubble_radius, color='skyblue', ec='dodgerblue', lw=2, zorder=5, 
    label=r'$\text{Bubble } (r = a)$'
)
ax.add_patch(bubble)

# 3. Simulate and Plot Downward Trajectories (LaTeX Legend Labels)
x_starts = np.linspace(0.05, 0.8, num_particles)
colors = plt.cm.plasma(np.linspace(0.2, 0.85, num_particles))

for i, x0 in enumerate(x_starts):
    px, py = simulate_downward_trajectory(
        a=bubble_radius, 
        U=far_field_velocity, 
        D=diffusion_coeff, 
        x0=x0, 
        y0=3.8, 
        seed=202 + i*17
    )
    ax.plot(px, py, color=colors[i], lw=1.8, label=rf'$\text{{Trajectory }} x_0/a = {x0:.2f}$', zorder=10)
    ax.scatter(px[0], py[0], color=colors[i], marker='o', s=30, zorder=11)

# Format Axes using LaTeX
ax.set_aspect('equal')
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-4, 4)
ax.set_xlabel(r'$\text{Dimensionless Horizontal Position } x/a$', fontsize=12)
ax.set_ylabel(r'$\text{Dimensionless Vertical Position } y/a$', fontsize=12)
ax.set_title(r'$\mathbf{\text{Random Walk 2D Stokes Flow}}$', fontsize=13, pad=12)
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='lower right', fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.show()
