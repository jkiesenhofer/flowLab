import numpy as np
import matplotlib.pyplot as plt

# --- Simulation & Physical Parameters ---
dt_normal = 0.001    # Physical time step
t_max = 3.5          # Total simulation timeframe

# Physical Constants
rho_w = 1000.0       # Density of water
r_p = 0.045e-3       # Particle radius
rho_p = 1150.0       
m_p = rho_p * (4.0/3.0) * np.pi * (r_p**3)

# Bubble Parameters
d_b = 1.0e-3         
r_0 = d_b / 2.0      # Characteristic length scale for normalization
bubble_pos = np.array([0.0, 0.0])  

# Initial Conditions
particle_pos = np.array([0.22e-3, 1.2e-3])  
particle_vel = np.array([0.0, -0.12])    

is_sliding = False
deformation_amplitude = 0.0

# Define the 4 target snapshot timestamps (seconds)
target_timesteps = [0.002, 0.005, 0.01, 0.02]
snapshot_data = {}  # Dictionary to cache position states for plotting

# --- Run the Core Simulation Loop to extract states ---
current_time = 0.0
step_idx = 0

# Track data points for rendering trajectories smoothly
path_x, path_y = [particle_pos[0]], [particle_pos[1]]

while current_time <= t_max + dt_normal:
    dt = dt_normal * 0.25 if current_time < 1.25 else dt_normal
    
    # Save closest state matching target intervals
    for t_step in target_timesteps:
        if abs(current_time - t_step) < dt * 0.51:
            snapshot_data[t_step] = {
                'pos': particle_pos.copy(),
                'traj_x': list(path_x),
                'traj_y': list(path_y),
                'is_sliding': is_sliding,
                'deform': deformation_amplitude
            }
            
    # Vector Mathematics 
    dx = particle_pos[0] - bubble_pos[0]
    dy = particle_pos[1] - bubble_pos[1]
    dist = np.sqrt(dx**2 + dy**2)
    
    nx, ny = dx / dist, dy / dist
    tx, ty = -ny, nx  

    if dist > (r_0 + r_p):
        u_fluid_x = -(-0.12) * (3/2) * (r_0**3) * (dx * dy) / (dist**5)
        u_fluid_y = (-0.12) * (1 - 0.5 * (r_0/dist)**3 + 1.5 * (r_0**3) * (dy**2) / (dist**5))
        particle_vel[0] = u_fluid_x
        particle_vel[1] = u_fluid_y
        deformation_amplitude = max(0.0, deformation_amplitude - 2.0 * dt)
    else:
        is_sliding = True
        v_tangential = np.dot(particle_vel, [tx, ty])
        if abs(v_tangential) < 0.02: 
            v_tangential = -0.09  
            
        particle_pos[0] = (r_0 + r_p) * nx
        particle_pos[1] = (r_0 + r_p) * ny
        particle_vel[0] = v_tangential * tx
        particle_vel[1] = v_tangential * ty
        deformation_amplitude = min(r_0 * 0.12, deformation_amplitude + 0.4 * dt)

    particle_pos += particle_vel * dt
    path_x.append(particle_pos[0])
    path_y.append(particle_pos[1])
    current_time += dt

# --- Plot Setup (4 Subplots Side-by-Side) ---
fig, axes = plt.subplots(1, 4, figsize=(16, 5), sharey=True, facecolor='#ffffff')
view_size_meters = 1.5e-3  
view_size_dimensionless = view_size_meters / r_0  # Normalized view limits

theta = np.linspace(0, 2*np.pi, 250)

for idx, (ax, t_val) in enumerate(zip(axes, target_timesteps)):
    ax.set_facecolor('#fdfdfd')
    ax.set_xlim(-view_size_dimensionless, view_size_dimensionless)
    ax.set_ylim(-view_size_dimensionless, view_size_dimensionless)
    ax.set_aspect('equal')
    ax.grid(True, color='#e5e5e5', alpha=0.5, linestyle='--')
    
    # Set dimensionless axis labels
    ax.set_xlabel(r'$x / r_0$', fontsize=10, color='#333333')
    if idx == 0:
        ax.set_ylabel(r'$y / r_0$', fontsize=10, color='#333333')
    
    # Extract historical states from run loop dictionary
    state = snapshot_data[t_val]
    p_pos = state['pos']
    d_amp = state['deform']
    
    # Scale variables to be dimensionless
    p_pos_dimless = p_pos / r_0
    traj_x_dimless = np.array(state['traj_x']) / r_0
    traj_y_dimless = np.array(state['traj_y']) / r_0
    d_amp_dimless = d_amp / r_0
    r_0_dimless = 1.0  # Normalized bubble radius is always 1
    
    # Regenerate mesh profile using dimensionless variables
    xb, yb = [], []
    nx_s, ny_s = p_pos[0] / np.linalg.norm(p_pos), p_pos[1] / np.linalg.norm(p_pos)
    p_angle = np.arctan2(ny_s, nx_s)
    if p_angle < 0: p_angle += 2 * np.pi

    for angle in theta:
        x_c = r_0_dimless * np.cos(angle)
        y_c = r_0_dimless * np.sin(angle)
        if state['is_sliding'] and d_amp > 0:
            ang_dist = np.abs(angle - p_angle)
            if ang_dist > np.pi: ang_dist = 2 * np.pi - ang_dist
            if ang_dist < np.pi/4:
                w = np.cos(ang_dist / (np.pi/4) * np.pi / 2.0)**2
                x_c -= w * d_amp_dimless * np.cos(p_angle)
                y_c -= w * d_amp_dimless * np.sin(p_angle)
        xb.append(x_c)
        yb.append(y_c)
        
    # Render spatial objects in dimensionless space
    ax.fill(xb, yb, color='#e3f2fd', alpha=0.8, edgecolor='#0288d1', linewidth=2, zorder=2)
    ax.plot(traj_x_dimless, traj_y_dimless, color='#f59e0b', linestyle='-', linewidth=1.5, alpha=0.7, zorder=3)
    ax.scatter(p_pos_dimless[0], p_pos_dimless[1], s=70, color='#38bdf8', edgecolors='#0369a1', linewidth=1.5, zorder=4)
    
    # Subplot titles
    ax.set_title(f"T = {t_val:.3f}s", fontsize=12, fontweight='bold', pad=12, color='#111111')
    
    # Adjust border parameters
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
        spine.set_linewidth(1.2)
    ax.tick_params(colors='#777777', labelsize=8)

plt.tight_layout()
plt.show()
