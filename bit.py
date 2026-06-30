import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Simulation Parameters ---
NUM_PARTICLES = 1050
DT = 0.05
NUM_STEPS = 250

# Bubble physical properties (2D Circle)
bubble_radius = 1.5
bubble_pos = np.array([0.0, -9.0])       # Starts at the bottom (X, Y)
bubble_vel = np.array([0.0, 0.0])        # Starts from rest (Vx, Vy)
buoyancy_accel = 0.08                     # Upward acceleration (along Y)
wobble_amplitude = 0.2                    # Lateral zig-zag amplitude
wobble_frequency = 2.5                    # Speed of the wobble

# Initialize Lagrangian particles (Distributed in the water column above)
np.random.seed(42)
particle_pos = np.random.uniform(-4, 4, (NUM_PARTICLES, 2))
particle_pos[:, 1] = np.random.uniform(-4, 8, NUM_PARTICLES) # Spread vertically along Y
particle_vel = np.random.uniform(-0.02, 0.02, (NUM_PARTICLES, 2))

# --- Set up the Plot ---
fig, ax = plt.subplots(figsize=(8, 8))

# Scatter plot for particles
particle_scatter = ax.scatter(particle_pos[:, 0], particle_pos[:, 1], 
                             c='royalblue', alpha=0.6, s=25, label='Particles')

# Circle patch for the rising bubble
bubble_patch = plt.Circle((bubble_pos[0], bubble_pos[1]), bubble_radius, 
                          color='deepskyblue', alpha=0.4, ec='dodgerblue', lw=2)
ax.add_patch(bubble_patch)

# Plot styling
ax.set_xlim([-6, 6])
ax.set_ylim([-10, 10])
ax.set_xlabel('X (Width)')
ax.set_ylabel('Y (Height / Rise Direction)')
ax.set_title('2D Buoyant Rising Bubble & Lagrangian Particles')
ax.grid(True, linestyle='--')
ax.set_aspect('equal') # Ensure the bubble stays a perfect circle visually

# --- Animation Update Function ---
time_elapsed = 0.0

def update(frame):
    global bubble_pos, bubble_vel, particle_pos, particle_vel, time_elapsed

    time_elapsed += DT

    # 1. Update Bubble Physics (Buoyancy + Horizontal Wobble)
    bubble_vel[1] += buoyancy_accel * DT  # Accelerate upward (Y-axis)
    if bubble_vel[1] > 0.4:               # Terminal velocity cap
        bubble_vel[1] = 0.4
        
    # Periodic horizontal oscillation (X-axis)
    bubble_vel[0] = wobble_amplitude * np.cos(wobble_frequency * time_elapsed)

    bubble_pos += bubble_vel

    # 2. Update Particle Positions
    particle_pos += particle_vel * DT

    # 3. 2D Collision Handling
    relative_pos = particle_pos - bubble_pos
    distances = np.linalg.norm(relative_pos, axis=1)
    collided_indices = np.where(distances <= bubble_radius)[0]

    for idx in collided_indices:
        # Normal unit vector pointing outwards from bubble center to particle
        normal = relative_pos[idx] / distances[idx]
        
        # Snap particle to the outer surface boundary
        particle_pos[idx] = bubble_pos + normal * bubble_radius
        
        # Relative velocity vector
        rel_vel = particle_vel[idx] - bubble_vel
        dot_product = np.dot(rel_vel, normal)
        
        if dot_product < 0:  # Push apart if they are moving into each other
            rel_vel_reflected = rel_vel - 1.3 * dot_product * normal
            particle_vel[idx] = rel_vel_reflected + bubble_vel

    # 4. Refresh Graphics
    # Update particle scatter positions
    particle_scatter.set_offsets(particle_pos)
    
    # Update bubble circle center position
    bubble_patch.set_center((bubble_pos[0], bubble_pos[1]))

    return particle_scatter, bubble_patch

# --- Run Animation ---
ani = animation.FuncAnimation(fig, update, frames=NUM_STEPS, interval=25, blit=False)
plt.show()
