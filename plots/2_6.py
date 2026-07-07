import numpy as np
import matplotlib.pyplot as plt

# --- Apply Your Custom Styling ---
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

# --- Physical Parameters ---
DT = 0.0015
NUM_STEPS = 350
NUM_BUBBLES = 15
NUM_PARTICLES = 60
BUBBLE_RADIUS = 0.0005    
PARTICLE_RADIUS = 0.00015 
HYDROPHOBIC_RANGE = 0.0002  
CAPTURE_THRESHOLD = BUBBLE_RADIUS + PARTICLE_RADIUS + HYDROPHOBIC_RANGE

TURB_INTENSITY_BUBBLE = 0.12
TURB_INTENSITY_PARTICLE = 0.07
TAU_BUBBLE = 0.015
TAU_PARTICLE = 0.008

# --- Initialization ---
np.random.seed(42)

bubble_pos = np.zeros((NUM_BUBBLES, 3))
bubble_pos[:, 0] = np.random.uniform(-0.003, 0.003, NUM_BUBBLES) 
bubble_pos[:, 1] = np.random.uniform(-0.003, 0.003, NUM_BUBBLES) 
bubble_pos[:, 2] = np.random.uniform(-0.014, -0.010, NUM_BUBBLES) 
bubble_vel = np.zeros((NUM_BUBBLES, 3))
bubble_terminal_v = np.random.uniform(0.10, 0.14, NUM_BUBBLES)
bubble_buoyancy_accel = 9.81 * np.random.uniform(1.3, 1.7, NUM_BUBBLES)

particle_pos = np.zeros((NUM_PARTICLES, 3))
particle_pos[:, 0] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 1] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 2] = np.random.uniform(-0.006, 0.008, NUM_PARTICLES) 
particle_vel = np.zeros((NUM_PARTICLES, 3))

particle_attached_to = np.full(NUM_PARTICLES, -1, dtype=int)
particle_phi = np.zeros(NUM_PARTICLES)
particle_theta = np.zeros(NUM_PARTICLES)

# Tracking array for free particles count over time
free_particles_history = []
time_array = np.arange(NUM_STEPS) * DT

# --- Run Simulation Loop ---
for step in range(NUM_STEPS):
    noise_b = np.random.normal(0, 1, (NUM_BUBBLES, 3))
    noise_p = np.random.normal(0, 1, (NUM_PARTICLES, 3))

    # 1. Bubble Kinematics
    z_below_terminal = bubble_vel[:, 2] < bubble_terminal_v
    bubble_vel[z_below_terminal, 2] += bubble_buoyancy_accel[z_below_terminal] * DT
    bubble_vel[~z_below_terminal, 2] = bubble_terminal_v[~z_below_terminal]
    bubble_vel += (-bubble_vel / TAU_BUBBLE) * DT + (TURB_INTENSITY_BUBBLE * np.sqrt(DT) * noise_b)
    bubble_pos += bubble_vel * DT

    # 2. Free Particle Kinematics
    free_mask = (particle_attached_to == -1)
    free_particles_history.append(np.sum(free_mask))
    
    if np.any(free_mask):
        particle_vel[free_mask] += (-particle_vel[free_mask] / TAU_PARTICLE) * DT + (TURB_INTENSITY_PARTICLE * np.sqrt(DT) * noise_p[free_mask])
        particle_pos[free_mask] += particle_vel[free_mask] * DT

    # 3. Collision Testing
    if np.any(free_mask):
        free_indices = np.where(free_mask)[0]
        diff = particle_pos[free_mask, np.newaxis, :] - bubble_pos[np.newaxis, :, :]
        distances = np.linalg.norm(diff, axis=2) 

        for i, p_idx in enumerate(free_indices):
            closest_b_idx = np.argmin(distances[i])
            if distances[i, closest_b_idx] <= CAPTURE_THRESHOLD:
                particle_attached_to[p_idx] = closest_b_idx
                rel_vec = diff[i, closest_b_idx]
                dist = distances[i, closest_b_idx]
                
                particle_phi[p_idx] = np.arccos(np.clip(rel_vec[2] / (dist + 1e-9), -1.0, 1.0))
                particle_theta[p_idx] = np.mod(np.arctan2(rel_vec[1], rel_vec[0]), 2 * np.pi)

    # 4. Attached Particle Constraints
    attached_mask = (particle_attached_to >= 0)
    if np.any(attached_mask):
        b_indices = particle_attached_to[attached_mask]
        total_r = BUBBLE_RADIUS + PARTICLE_RADIUS
        phi_vals = particle_phi[attached_mask]
        theta_vals = particle_theta[attached_mask]
        
        particle_pos[attached_mask, 0] = bubble_pos[b_indices, 0] + total_r * np.sin(phi_vals) * np.cos(theta_vals)
        particle_pos[attached_mask, 1] = bubble_pos[b_indices, 1] + total_r * np.sin(phi_vals) * np.sin(theta_vals)
        particle_pos[attached_mask, 2] = bubble_pos[b_indices, 2] + total_r * np.cos(phi_vals)

free_particles_history = np.array(free_particles_history)

# --- Compute Flotation Reaction Rate k (min^-1) ---
# Using a central difference rolling window to smooth stochastic stepping anomalies
window = 20
rate_k = np.zeros_like(free_particles_history, dtype=float)

for t in range(window, NUM_STEPS - window):
    dN = free_particles_history[t - window] - free_particles_history[t + window]
    dt_window = 2 * window * DT
    N_current = free_particles_history[t]
    
    if N_current > 0:
        # k = -(1/N) * (dN/dt) * 60 (to convert sec^-1 to min^-1)
        rate_k[t] = (dN / dt_window) / N_current * 60
    else:
        rate_k[t] = 0.0

# Trim boundaries influenced by window limits
valid_idx = slice(window, NUM_STEPS - window)

# --- Plotting ---
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot 1: Flotation Kinetic Rate
color = 'crimson'
ax1.set_xlabel('Time (s)')
ax1.set_ylabel(r'Reaction Rate $k$ ($\mathrm{min}^{-1}$)', color=color)
ax1.plot(time_array[valid_idx], rate_k[valid_idx], color=color, lw=2.5, label='Flotation Rate ($k$)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle=':', alpha=0.6)

# Plot 2: Remaining Free Particles (Twin Axis for physical context)
ax2 = ax1.twinx()
color = 'royalblue'
ax2.set_ylabel('Remaining Free Particles', color=color)
ax2.plot(time_array, free_particles_history, color=color, linestyle='--', lw=2, label='Free Particles')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Instantaneous Flotation Kinetics over Time')
fig.tight_layout()
plt.show()
