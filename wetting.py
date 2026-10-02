import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.titlesize": 14
})

# ==========================================
# 1. Simulation Parameters & Physical Scaling
# ==========================================
Nx, Ny = 140, 100          # Grid dimensions
dx = dy = 0.5              # Spatial step (grid units)
dt = 0.00015               # Stable time step for explicit Cahn-Hilliard
n_steps = 7000             # Total iterations
frame_interval = 70        # Frame caching interval

# Physical length scale mapping: 1 grid unit = 0.08 mm
scale_mm = 0.08 

sigma = 4.0                # Increased surface tension (rigidity & stronger capillary pull)
epsilon = 1.0              # Interface width
M = 1.0                    # Mobility parameter
theta_eq_deg = 135.0       # Contact angle of liquid phase at particle surface
theta_eq = np.radians(theta_eq_deg)

# Lateral shear / driving force
F_ext_x = 0.04

# Particle Properties (0.8 mm diameter -> r_p = 0.4 mm -> 5.0 grid units)
r_p = 5.0                  

# Bubble Geometry (2.0 mm diameter -> radius = 1.0 mm -> 12.5 grid units)
radius = 12.5              
center_x = (Nx * dx) / 2.0
center_y = (Ny * dy) / 2.0 - 6.0

# Initial Offset Position: Placed with an offset on the upper-right shoulder of the bubble
offset_angle = np.pi / 4.0   # 45 degrees (upper-right shoulder)
particle_x = center_x + radius * np.cos(offset_angle)
particle_y = center_y + radius * np.sin(offset_angle)

# Forces & Kinematics parameters
g = 30.0                   # Gravitational acceleration
f_cap_coeff = 2.5          # Capillary force coupling strength multiplier
v_p_y = 1.0                # Initial vertical velocity
v_p_x = 1.0                # Initial horizontal velocity
particle_mass = 10.0       # Effective particle mass

x = np.arange(Nx) * dx
y = np.arange(Ny) * dy
X, Y = np.meshgrid(x, y, indexing='ij')

# Field initialization: Liquid matrix (+1), Bubble region (-1)
dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
phi = np.tanh((dist - radius) / (np.sqrt(2.0) * epsilon))

# Initial Particle Mask
dist_p = np.sqrt((X - particle_x)**2 + (Y - particle_y)**2)
solid_mask = dist_p <= r_p
phi[solid_mask] = 0.0

# ==========================================
# 2. Physics & Boundary Functions
# ==========================================
def update_particle_mask(px, py):
    d_p = np.sqrt((X - px)**2 + (Y - py)**2)
    s_mask = d_p <= r_p
    return d_p, s_mask

def compute_capillary_force(phi_field, px, py):
    n_samples = 72
    angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
    sample_r = r_p + 0.5 * dx
    
    fx_sum, fy_sum = 0.0, 0.0
    for ang in angles:
        sx = px + sample_r * np.cos(ang)
        sy = py + sample_r * np.sin(ang)
        
        ix = np.clip(int(np.round(sx / dx)), 1, Nx - 2)
        iy = np.clip(int(np.round(sy / dy)), 1, Ny - 2)
        
        grad_x = (phi_field[ix + 1, iy] - phi_field[ix - 1, iy]) / (2 * dx)
        grad_y = (phi_field[ix, iy + 1] - phi_field[ix, iy - 1]) / (2 * dy)
        
        phi_val = phi_field[ix, iy]
        fx_sum -= grad_x * (1.0 - phi_val**2)
        fy_sum -= grad_y * (1.0 - phi_val**2)
        
    return f_cap_coeff * sigma * fx_sum / n_samples, f_cap_coeff * sigma * fy_sum / n_samples

def apply_boundary_conditions(phi_field, eps, theta_e, d_p, mask):
    phi_field[:, -1] = phi_field[:, -2]
    phi_field[:, 0]  = phi_field[:, 1]
    phi_field[0, :]  = phi_field[1, :]
    phi_field[-1, :] = phi_field[-2, :]
    
    surface_band = (d_p > r_p) & (d_p <= r_p + 1.5 * dx)
    phi_field[surface_band] -= dt * (1.0 / eps) * np.cos(theta_e) * (1.0 - phi_field[surface_band]**2)
    phi_field[mask] = 0.0
    return phi_field

def compute_chemical_potential(phi_field, eps, sig, mask):
    df_dphi = (3.0 * sig / (2.0 * eps)) * phi_field * (phi_field**2 - 1.0)
    lap_phi = np.zeros_like(phi_field)
    
    lap_phi[1:-1, 1:-1] = (
        (phi_field[2:, 1:-1] + phi_field[:-2, 1:-1] + 
         phi_field[1:-1, 2:] + phi_field[1:-1, :-2] - 4.0 * phi_field[1:-1, 1:-1]) / (dx**2)
    )
    
    mu = df_dphi - 1.5 * sig * eps * lap_phi
    mu[mask] = 0.0
    return mu

# ==========================================
# 3. Dynamic Integration Loop
# ==========================================
phi_history = []
particle_pos_history = []
t_hist, angle_left, angle_right = [], [], []

print("Simulating high surface tension (sigma=4.0) case...")
for step in range(n_steps):
    f_cap_x, f_cap_y = compute_capillary_force(phi, particle_x, particle_y)
    
    acc_x = f_cap_x / particle_mass
    acc_y = (-particle_mass * g + f_cap_y) / particle_mass
    
    v_p_x += acc_x * dt
    v_p_y += acc_y * dt
    particle_x += v_p_x * dt
    particle_y += v_p_y * dt
    
    if particle_y - r_p <= dy:
        particle_y = dy + r_p
        v_p_y = 0.0

    dist_p, solid_mask = update_particle_mask(particle_x, particle_y)
    
    phi = apply_boundary_conditions(phi, epsilon, theta_eq, dist_p, solid_mask)
    mu = compute_chemical_potential(phi, epsilon, sigma, solid_mask)
    
    dphi_dx = np.zeros_like(phi)
    dphi_dx[1:-1, :] = (phi[2:, :] - phi[:-2, :]) / (2 * dx)
    
    lap_mu = np.zeros_like(mu)
    lap_mu[1:-1, 1:-1] = (
        (mu[2:, 1:-1] + mu[:-2, 1:-1] + 
         mu[1:-1, 2:] + mu[1:-1, :-2] - 4.0 * mu[1:-1, 1:-1]) / (dx**2)
    )
    
    phi[1:-1, 1:-1] += dt * (M * lap_mu[1:-1, 1:-1] - F_ext_x * dphi_dx[1:-1, 1:-1])
    phi[solid_mask] = 0.0
    
    if step % frame_interval == 0:
        phi_history.append(phi.copy())
        particle_pos_history.append((particle_x, particle_y))
        
        # Ring sampling for contact angles
        n_samples = 360
        angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
        sample_r = r_p + 1.2 * dx
        sx = np.clip((particle_x + sample_r * np.cos(angles)) / dx, 0, Nx - 1).astype(int)
        sy = np.clip((particle_y + sample_r * np.sin(angles)) / dy, 0, Ny - 1).astype(int)
        crossings = np.where(np.diff(np.sign(phi[sx, sy])))[0]
        
        if len(crossings) >= 2:
            tl = abs(180.0 - np.degrees(angles[crossings[0]])) % 180.0
            tr = abs(180.0 - np.degrees(angles[crossings[-1]])) % 180.0
        else:
            tl, tr = np.nan, np.nan
            
        t_hist.append(step * dt)
        angle_left.append(tl)
        angle_right.append(tr)

# ==========================================
# 4. GIF Export (Physical mm Axes)
# ==========================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

X_mm = X * scale_mm
Y_mm = Y * scale_mm

def update(frame):
    for ax in axes:
        ax.clear()
        
    current_phi = phi_history[frame]
    px, py = particle_pos_history[frame]
    current_time = frame * frame_interval * dt
    
    contour = axes[0].contourf(X_mm, Y_mm, current_phi, levels=30, cmap='RdBu', vmin=-1.0, vmax=1.0)
    axes[0].contour(X_mm, Y_mm, current_phi, levels=[0], colors='black', linewidths=2)
    
    particle_circle = plt.Circle((px * scale_mm, py * scale_mm), r_p * scale_mm, color='gray', ec='black', lw=1.5, zorder=5)
    axes[0].add_patch(particle_circle)
    
    axes[0].set_title(f"High Surface Tension ($\sigma=4.0$) Slide (t = {current_time:.3f} s)")
    axes[0].set_xlabel("X (mm)")
    axes[0].set_ylabel("Y (mm)")
    axes[0].set_aspect('equal')
    
    valid_idx = ~np.isnan(angle_left[:frame+1])
    axes[1].plot(np.array(t_hist[:frame+1])[valid_idx], np.array(angle_left[:frame+1])[valid_idx], 'b-', label=r'Left Contact Angle ($\theta_{rec}$)')
    axes[1].plot(np.array(t_hist[:frame+1])[valid_idx], np.array(angle_right[:frame+1])[valid_idx], 'r-', label=r'Right Contact Angle ($\theta_{adv}$)')
    axes[1].axhline(y=theta_eq_deg, color='g', linestyle='--', label=f'Equilibrium ({theta_eq_deg}°)')
    axes[1].set_title("Dynamic Contact Angle")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Contact Angle (°)")
    axes[1].set_xlim(0, n_steps * dt)
    axes[1].set_ylim(0, 180)
    axes[1].grid(True, alpha=0.4)
    axes[1].legend(loc='upper right')
    
    plt.tight_layout()

ani = animation.FuncAnimation(fig, update, frames=len(phi_history), interval=50)
ani.save("bubble_high_sigma_slide.gif", writer="pillow", fps=20, dpi=150)
plt.close(fig)

print("Saved animation to 'bubble_high_sigma_slide.gif'")
