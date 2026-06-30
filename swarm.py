import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# --- Physical Parameters (SI Units: Meters, Seconds, Kg) ---
DT = 0.0015
NUM_STEPS = 350

# Entity Counts
NUM_BUBBLES = 15
NUM_PARTICLES = 60

# Dimensions
BUBBLE_RADIUS = 0.0005    # 0.5 mm
PARTICLE_RADIUS = 0.00015 # 0.15 mm

# Strong Hydrophobicity Parameters
HYDROPHOBIC_RANGE = 0.0002  # Enhanced 0.20 mm attraction zone
CAPTURE_THRESHOLD = BUBBLE_RADIUS + PARTICLE_RADIUS + HYDROPHOBIC_RANGE

# High-Intensity Turbulence Parameters
TURB_INTENSITY_BUBBLE = 0.12
TURB_INTENSITY_PARTICLE = 0.07
TAU_BUBBLE = 0.015
TAU_PARTICLE = 0.008

# --- State Arrays Setup (Vectorized Architecture) ---
np.random.seed(42)

# Bubbles Initialization
bubble_pos = np.zeros((NUM_BUBBLES, 3))
bubble_pos[:, 0] = np.random.uniform(-0.003, 0.003, NUM_BUBBLES) # X dispersion
bubble_pos[:, 1] = np.random.uniform(-0.003, 0.003, NUM_BUBBLES) # Y dispersion
bubble_pos[:, 2] = np.random.uniform(-0.014, -0.010, NUM_BUBBLES) # Z bottom pool
bubble_vel = np.zeros((NUM_BUBBLES, 3))

bubble_terminal_v = np.random.uniform(0.10, 0.14, NUM_BUBBLES)
bubble_buoyancy_accel = 9.81 * np.random.uniform(1.3, 1.7, NUM_BUBBLES)

# Particles Initialization
particle_pos = np.zeros((NUM_PARTICLES, 3))
particle_pos[:, 0] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 1] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 2] = np.random.uniform(-0.006, 0.008, NUM_PARTICLES) # Spread throughout column
particle_vel = np.zeros((NUM_PARTICLES, 3))

# Attachment Trackers: -1 means free, >= 0 indicates index of owner bubble
particle_attached_to = np.full(NUM_PARTICLES, -1, dtype=int)
particle_phi = np.zeros(NUM_PARTICLES)
particle_theta = np.zeros(NUM_PARTICLES)

# History storage for trajectories
bubble_histories = [[] for _ in range(NUM_BUBBLES)]
particle_histories = [[] for _ in range(NUM_PARTICLES)]

# --- Set up 3D Canvas ---
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=20, azim=45)

# Render initial positions
bubble_scatters = ax.scatter(bubble_pos[:, 0]*1000, bubble_pos[:, 1]*1000, bubble_pos[:, 2]*1000,
                             color='darkturquoise', s=45, edgecolors='black', label='Bubble Swarm', zorder=4)

particle_scatters = ax.scatter(particle_pos[:, 0]*1000, particle_pos[:, 1]*1000, particle_pos[:, 2]*1000,
                               color='royalblue', s=20, edgecolors='black', label='Particle Feed', zorder=5)

# Setup trajectory lines arrays
bubble_lines = [ax.plot([], [], [], color='deepskyblue', lw=1.0, alpha=0.4)[0] for _ in range(NUM_BUBBLES)]
particle_lines = [ax.plot([], [], [], color='crimson', linestyle='--', lw=0.8, alpha=0.4)[0] for _ in range(NUM_PARTICLES)]

# Format Plot Box
ax.set_xlim([-6.0, 6.0])
ax.set_ylim([-6.0, 6.0])
ax.set_zlim([-15, 15])
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm / Rise Height)')
#ax.set_title('Turbulent Multi-Phase Flotation Column (Vectorized Swarm)')
ax.legend(loc='upper left')
ax.grid(True, linestyle=':', alpha=0.5)

# --- Animation Loop ---
def update(frame):
    global bubble_pos, bubble_vel, particle_pos, particle_vel, particle_attached_to, particle_phi, particle_theta

    # Generate spatial stochastic white noise blocks
    noise_b = np.random.normal(0, 1, (NUM_BUBBLES, 3))
    noise_p = np.random.normal(0, 1, (NUM_PARTICLES, 3))

    # 1. Vectorized Bubble Kinematics
    z_below_terminal = bubble_vel[:, 2] < bubble_terminal_v
    bubble_vel[z_below_terminal, 2] += bubble_buoyancy_accel[z_below_terminal] * DT
    bubble_vel[~z_below_terminal, 2] = bubble_terminal_v[~z_below_terminal]

    # Apply turbulent random walk differential to bubbles
    bubble_vel += (-bubble_vel / TAU_BUBBLE) * DT + (TURB_INTENSITY_BUBBLE * np.sqrt(DT) * noise_b)
    bubble_pos += bubble_vel * DT

    # 2. Vectorized Free Particle Kinematics
    free_mask = (particle_attached_to == -1)
    if np.any(free_mask):
        particle_vel[free_mask] += (-particle_vel[free_mask] / TAU_PARTICLE) * DT + (TURB_INTENSITY_PARTICLE * np.sqrt(DT) * noise_p[free_mask])
        particle_pos[free_mask] += particle_vel[free_mask] * DT

    # 3. Vectorized Proximity Collision Testing
    if np.any(free_mask):
        free_indices = np.where(free_mask)[0]
        # Compare distance matrix fields using broad-casting hooks
        # Shape: (NUM_FREE_PARTICLES, NUM_BUBBLES, 3)
        diff = particle_pos[free_mask, np.newaxis, :] - bubble_pos[np.newaxis, :, :]
        distances = np.linalg.norm(diff, axis=2) # Shape: (NUM_FREE_PARTICLES, NUM_BUBBLES)

        # Look for minimum distance matches below the hydrophobicity ceiling
        for i, p_idx in enumerate(free_indices):
            closest_b_idx = np.argmin(distances[i])
            if distances[i, closest_b_idx] <= CAPTURE_THRESHOLD:
                # Intercept established
                particle_attached_to[p_idx] = closest_b_idx
                rel_vec = diff[i, closest_b_idx]
                dist = distances[i, closest_b_idx]
                
                # Assign static lock parameters
                particle_phi[p_idx] = np.arccos(np.clip(rel_vec[2] / (dist + 1e-9), -1.0, 1.0))
                particle_theta[p_idx] = np.mod(np.arctan2(rel_vec[1], rel_vec[0]), 2 * np.pi)

    # 4. Vectorized Attached Particle Constraints
    attached_mask = (particle_attached_to >= 0)
    if np.any(attached_mask):
        b_indices = particle_attached_to[attached_mask]
        total_r = BUBBLE_RADIUS + PARTICLE_RADIUS
        
        phi_vals = particle_phi[attached_mask]
        theta_vals = particle_theta[attached_mask]
        
        # Reposition items instantly tracking parent bubble shell coordinates
        particle_pos[attached_mask, 0] = bubble_pos[b_indices, 0] + total_r * np.sin(phi_vals) * np.cos(theta_vals)
        particle_pos[attached_mask, 1] = bubble_pos[b_indices, 1] + total_r * np.sin(phi_vals) * np.sin(theta_vals)
        particle_pos[attached_mask, 2] = bubble_pos[b_indices, 2] + total_r * np.cos(phi_vals)

    # 5. Document History Trajectories & Render Frame
    bubble_scatters._offsets3d = (bubble_pos[:, 0]*1000, bubble_pos[:, 1]*1000, bubble_pos[:, 2]*1000)
    
    p_colors = np.where(particle_attached_to >= 0, 'crimson', 'royalblue')
    particle_scatters.set_color(p_colors)
    particle_scatters._offsets3d = (particle_pos[:, 0]*1000, particle_pos[:, 1]*1000, particle_pos[:, 2]*1000)

    # Draw trajectories
    for b in range(NUM_BUBBLES):
        bubble_histories[b].append(bubble_pos[b] * 1000)
        b_t = np.array(bubble_histories[b])
        bubble_lines[b].set_data(b_t[:, 0], b_t[:, 1])
        bubble_lines[b].set_3d_properties(b_t[:, 2])

    for p in range(NUM_PARTICLES):
        particle_histories[p].append(particle_pos[p] * 1000)
        p_t = np.array(particle_histories[p])
        particle_lines[p].set_data(p_t[:, 0], p_t[:, 1])
        particle_lines[p].set_3d_properties(p_t[:, 2])

    return bubble_scatters, particle_scatters

# --- Execute Animation ---
ani = animation.FuncAnimation(fig, update, frames=NUM_STEPS, interval=15, blit=False)
plt.show()
