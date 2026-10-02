import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# ==========================================
# 1. Simulation Parameters & Physical Scaling
# ==========================================
Nx, Ny = 140, 110          # Grid dimensions
dx = dy = 0.5              # Spatial step (grid units)
dt = 0.00001               # Highly conservative time step for stability
n_steps = 15000            # Total iterations
frame_interval = 75        # Frame caching interval

# Physical length scale mapping: 1 grid unit = 0.08 mm
scale_mm = 0.08 

sigma = 2.0                # Controlled surface tension coefficient
rho_l, rho_g = 1.0, 0.1    # Liquid and gas densities
mu_l, mu_g = 0.8, 0.08     # Higher dynamic viscosity for damping oscillations

theta_eq_deg = 135.0       # Equilibrium contact angle
theta_eq = np.radians(theta_eq_deg)

# Particle Properties (0.8 mm diameter -> r_p = 0.4 mm -> 3.0 grid units)
r_p = 3.0                  

# Bubble Geometry (2.0 mm diameter -> radius = 1.0 mm -> 12.5 grid units)
radius = 12.5              
center_x = (Nx * dx) / 2.0
center_y = 35.0            # Placed lower in the domain to allow buoyant rise

# Initial Offset Position: Placed on the upper-right shoulder of the bubble
offset_angle = np.pi / 4.0   # 45 degrees
particle_x = center_x + radius * np.cos(offset_angle)
particle_y = center_y + radius * np.sin(offset_angle)

# Forces & Kinematics parameters
g = 10.0                   # Gravitational acceleration
f_cap_coeff = 1.5          # Capillary force coupling strength
v_p_y = 0.0                # Initial vertical velocity
v_p_x = 0.0                # Initial horizontal velocity
particle_mass = 20.0        # Effective particle mass

x = np.arange(Nx) * dx
y = np.arange(Ny) * dy
X, Y = np.meshgrid(x, y, indexing='ij')

# VOF Field initialization: Liquid matrix (F = 1), Bubble gas region (F = 0)
dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
F = 0.5 * (1.0 - np.tanh((dist - radius) / (1.5 * dx)))

# Velocity and Pressure fields initialization
u = np.zeros((Nx, Ny))
v = np.zeros((Nx, Ny))
p = np.zeros((Nx, Ny))

# Initial Particle Mask
dist_p = np.sqrt((X - particle_x)**2 + (Y - particle_y)**2)
solid_mask = dist_p <= r_p
F[solid_mask] = 0.0
u[solid_mask] = 0.0
v[solid_mask] = 0.0

# ==========================================
# 2. Navier-Stokes Solver & VOF Functions
# ==========================================
def update_particle_mask(px, py):
    d_p = np.sqrt((X - px)**2 + (Y - py)**2)
    s_mask = d_p <= r_p
    return d_p, s_mask

def compute_capillary_force(F_field, px, py):
    n_samples = 72
    angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
    sample_r = r_p + 0.5 * dx
    
    fx_sum, fy_sum = 0.0, 0.0
    for ang in angles:
        sx = px + sample_r * np.cos(ang)
        sy = py + sample_r * np.sin(ang)
        
        ix = np.clip(int(np.round(sx / dx)), 1, Nx - 2)
        iy = np.clip(int(np.round(sy / dy)), 1, Ny - 2)
        
        gx = (F_field[ix + 1, iy] - F_field[ix - 1, iy]) / (2 * dx)
        gy = (F_field[ix, iy + 1] - F_field[ix, iy - 1]) / (2 * dy)
        
        f_val = F_field[ix, iy]
        fx_sum += gx * (1.0 - 2.0 * f_val)
        fy_sum += gy * (1.0 - 2.0 * f_val)
        
    return f_cap_coeff * sigma * fx_sum / n_samples, f_cap_coeff * sigma * fy_sum / n_samples

def navier_stokes_step(u, v, p, F, mask):
    """
    Solves 2D incompressible Navier-Stokes with robust NaN sanitization.
    """
    rho = F * rho_l + (1.0 - F) * rho_g
    mu = F * mu_l + (1.0 - F) * mu_g
    
    # Interface curvature and CSF surface tension force
    gx = np.zeros_like(F)
    gy = np.zeros_like(F)
    gx[1:-1, :] = (F[2:, :] - F[:-2, :]) / (2 * dx)
    gy[:, 1:-1] = (F[:, 2:] - F[:, :-2]) / (2 * dy)
    gx[mask] = 0.0
    gy[mask] = 0.0
    
    mag = np.sqrt(gx**2 + gy**2) + 1e-8
    nx, ny = gx / mag, gy / mag
    
    div_n = np.zeros_like(F)
    div_n[1:-1, 1:-1] = (
        (nx[2:, 1:-1] - nx[:-2, 1:-1]) / (2 * dx) +
        (ny[1:-1, 2:] - ny[1:-1, :-2]) / (2 * dy)
    )
    kappa = -div_n
    kappa[mask] = 0.0
    
    f_st_x = sigma * kappa * gx
    f_st_y = sigma * kappa * gy
    
    # Momentum Predictor Step
    u_star = u.copy()
    v_star = v.copy()
    
    lap_u = np.zeros_like(u)
    lap_v = np.zeros_like(v)
    lap_u[1:-1, 1:-1] = (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] - 4.0 * u[1:-1, 1:-1]) / (dx**2)
    lap_v[1:-1, 1:-1] = (v[2:, 1:-1] + v[:-2, 1:-1] + v[1:-1, 2:] + v[1:-1, :-2] - 4.0 * v[1:-1, 1:-1]) / (dx**2)
    
    du_dx, du_dy = np.zeros_like(u), np.zeros_like(u)
    dv_dx, dv_dy = np.zeros_like(v), np.zeros_like(v)
    
    du_dx[1:-1, :] = (u[2:, :] - u[:-2, :]) / (2 * dx)
    du_dy[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2 * dy)
    dv_dx[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2 * dx)
    dv_dy[:, 1:-1] = (v[:, 2:] - v[:, :-2]) / (2 * dy)
    
    rho_node = np.maximum(rho, 0.05)
    gravity_y = -g + ((rho_l - rho_node) / rho_node) * g
    
    u_star[1:-1, 1:-1] += dt * (
        - (u[1:-1, 1:-1] * du_dx[1:-1, 1:-1] + v[1:-1, 1:-1] * du_dy[1:-1, 1:-1])
        + (mu[1:-1, 1:-1] / rho_node[1:-1, 1:-1]) * lap_u[1:-1, 1:-1]
        + (f_st_x[1:-1, 1:-1] / rho_node[1:-1, 1:-1])
    )
    
    v_star[1:-1, 1:-1] += dt * (
        - (u[1:-1, 1:-1] * dv_dx[1:-1, 1:-1] + v[1:-1, 1:-1] * dv_dy[1:-1, 1:-1])
        + (mu[1:-1, 1:-1] / rho_node[1:-1, 1:-1]) * lap_v[1:-1, 1:-1]
        + gravity_y[1:-1, 1:-1]
        + (f_st_y[1:-1, 1:-1] / rho_node[1:-1, 1:-1])
    )
    
    # Pressure Poisson Equation Solver
    rhs = np.zeros_like(p)
    rhs[1:-1, 1:-1] = (rho_node[1:-1, 1:-1] / dt) * (
        (u_star[2:, 1:-1] - u_star[:-2, 1:-1]) / (2 * dx) +
        (v_star[1:-1, 2:] - v_star[1:-1, :-2]) / (2 * dy)
    )
    
    p_new = p.copy()
    for _ in range(10):
        p_new[1:-1, 1:-1] = 0.25 * (
            p_new[2:, 1:-1] + p_new[:-2, 1:-1] +
            p_new[1:-1, 2:] + p_new[1:-1, :-2] -
            dx**2 * rhs[1:-1, 1:-1]
        )
    p = p_new
    
    dp_dx = np.zeros_like(p)
    dp_dy = np.zeros_like(p)
    dp_dx[1:-1, :] = (p[2:, :] - p[:-2, :]) / (2 * dx)
    dp_dy[:, 1:-1] = (p[:, 2:] - p[:, :-2]) / (2 * dy)
    
    u_new = u_star - (dt / rho_node) * dp_dx
    v_new = v_star - (dt / rho_node) * dp_dy
    
    # Sanitize outputs against NaN/infs
    u_new = np.nan_to_num(u_new, nan=0.0, posinf=0.0, neginf=0.0)
    v_new = np.nan_to_num(v_new, nan=0.0, posinf=0.0, neginf=0.0)
    p = np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0)
    
    u_new[mask] = 0.0
    v_new[mask] = 0.0
    return u_new, v_new, p

def conservative_vof_advection(F_field, u_field, v_field, mask):
    F_new = F_field.copy()
    u_face = 0.5 * (u_field[:-1, :] + u_field[1:, :])
    v_face = 0.5 * (v_field[:, :-1] + v_field[:, 1:])
    
    flux_x = np.where(u_face >= 0, u_face * F_field[:-1, :], u_face * F_field[1:, :])
    flux_y = np.where(v_face >= 0, v_face * F_field[:, :-1], v_face * F_field[:, 1:])
    
    F_new[1:-1, 1:-1] = (F_field[1:-1, 1:-1] 
                         - (dt / dx) * (flux_x[1:, 1:-1] - flux_x[:-1, 1:-1])
                         - (dt / dy) * (flux_y[1:-1, 1:] - flux_y[1:-1, :-1]))
    
    F_new = np.nan_to_num(F_new, nan=1.0, posinf=1.0, neginf=0.0)
    F_new[mask] = 0.0
    return np.clip(F_new, 0.0, 1.0)

def apply_vof_boundary_conditions(F_field, theta_e, d_p, mask):
    F_field[:, -1] = F_field[:, -2]
    F_field[:, 0]  = F_field[:, 1]
    F_field[0, :]  = F_field[1, :]
    F_field[-1, :] = F_field[-2, :]
    
    surface_band = (d_p > r_p) & (d_p <= r_p + 1.5 * dx)
    F_field[surface_band] -= dt * np.cos(theta_e) * (F_field[surface_band] * (1.0 - F_field[surface_band]))
    F_field = np.clip(F_field, 0.0, 1.0)
    F_field[mask] = 0.0
    return F_field

def extract_particle_contact_angles(F_field, px, py):
    n_samples = 360
    angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
    sample_r = r_p + 1.2 * dx
    
    sample_x = px + sample_r * np.cos(angles)
    sample_y = py + sample_r * np.sin(angles)
    
    ix = np.clip((sample_x / dx).astype(int), 0, Nx - 1)
    iy = np.clip((sample_y / dy).astype(int), 0, Ny - 1)
    
    f_ring = F_field[ix, iy] - 0.5
    crossings = np.where(np.diff(np.sign(f_ring)))[0]
    
    if len(crossings) < 2:
        return np.nan, np.nan
    
    angle_l_deg = np.degrees(angles[crossings[0]])
    angle_r_deg = np.degrees(angles[crossings[-1]])
    
    theta_l = abs(180.0 - angle_l_deg) % 180.0
    theta_r = abs(180.0 - angle_r_deg) % 180.0
    
    return theta_l, theta_r

# ==========================================
# 3. Dynamic Integration Loop
# ==========================================
F_history = []
particle_pos_history = []
t_hist, angle_left, angle_right = [], [], []

print("Simulating stable buoyant bubble rise with Navier-Stokes VOF...")
for step in range(n_steps):
    f_cap_x, f_cap_y = compute_capillary_force(F, particle_x, particle_y)
    
    acc_x = f_cap_x / particle_mass
    acc_y = f_cap_y / particle_mass
    
    v_p_x += acc_x * dt
    v_p_y += acc_y * dt
    particle_x += v_p_x * dt
    particle_y += v_p_y * dt
    
    particle_x = np.clip(particle_x, r_p + dx, (Nx - 1) * dx - r_p)
    particle_y = np.clip(particle_y, r_p + dy, (Ny - 1) * dy - r_p)

    dist_p, solid_mask = update_particle_mask(particle_x, particle_y)
    
    u, v, p = navier_stokes_step(u, v, p, F, solid_mask)
    
    F = conservative_vof_advection(F, u, v, solid_mask)
    F = apply_vof_boundary_conditions(F, theta_eq, dist_p, solid_mask)
    
    if step % frame_interval == 0:
        F_history.append(F.copy())
        particle_pos_history.append((particle_x, particle_y))
        
        tl, tr = extract_particle_contact_angles(F, particle_x, particle_y)
        t_hist.append(step * dt)
        angle_left.append(tl)
        angle_right.append(tr)

# ==========================================
# 4. GIF Export
# ==========================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
X_mm = X * scale_mm
Y_mm = Y * scale_mm

def update(frame):
    for ax in axes:
        ax.clear()
        
    current_F = F_history[frame]
    px, py = particle_pos_history[frame]
    current_time = frame * frame_interval * dt
    
    contour = axes[0].contourf(X_mm, Y_mm, current_F, levels=30, cmap='Blues_r', vmin=0.0, vmax=1.0)
    axes[0].contour(X_mm, Y_mm, current_F, levels=[0.5], colors='black', linewidths=2)
    
    particle_circle = plt.Circle((px * scale_mm, py * scale_mm), r_p * scale_mm, color='gray', ec='black', lw=1.5, zorder=5)
    axes[0].add_patch(particle_circle)
    
    axes[0].set_title(f"Buoyant Bubble Rise (t = {current_time:.3f} s)")
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

ani = animation.FuncAnimation(fig, update, frames=len(F_history), interval=50)
ani.save("vof_buoyant_bubble.gif", writer="pillow", fps=20, dpi=150)
plt.close(fig)

print("Saved buoyant bubble animation to 'vof_buoyant_bubble.gif'")
