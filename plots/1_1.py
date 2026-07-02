import numpy as np
import matplotlib.pyplot as plt

# --- Set up Matplotlib style matching your LaTeX config ---
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.titlesize": 14
})

# --- Simulation Parameters (Matching your original scale) ---
DT = 0.0015
NUM_STEPS = 600       
NUM_PARTICLES = 150   
TAU_PARTICLE = 0.008
TURB_INTENSITY_PARTICLE = 0.07

np.random.seed(42)

# Initializing particle fields
particle_pos = np.zeros((NUM_PARTICLES, 3))
particle_pos[:, 0] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 1] = np.random.uniform(-0.004, 0.004, NUM_PARTICLES)
particle_pos[:, 2] = np.random.uniform(-0.010, 0.010, NUM_PARTICLES) 
particle_vel = np.zeros((NUM_PARTICLES, 3))

# Storage arrays to track fluctuations across time
all_z_positions = []
all_u_fluc = []  
all_v_fluc = []  
all_w_fluc = []  

# --- 1. Run Simulation and Track Fluctuations ---
for step in range(NUM_STEPS):
    noise_p = np.random.normal(0, 1, (NUM_PARTICLES, 3))
    
    # Kinematics Update
    particle_vel += (-particle_vel / TAU_PARTICLE) * DT + (TURB_INTENSITY_PARTICLE * np.sqrt(DT) * noise_p)
    particle_pos += particle_vel * DT
    
    # Calculate spatial mean flow profile at this instant
    mean_u = np.mean(particle_vel[:, 0])
    mean_v = np.mean(particle_vel[:, 1])
    mean_w = np.mean(particle_vel[:, 2])
    
    # Deviations/Fluctuations from mean flow (u', v', w')
    u_prime = particle_vel[:, 0] - mean_u
    v_prime = particle_vel[:, 1] - mean_v
    w_prime = particle_vel[:, 2] - mean_w
    
    # Convert Z positions to millimeters for graphing context
    all_z_positions.extend(particle_pos[:, 2] * 1000)
    all_u_fluc.extend(u_prime)
    all_v_fluc.extend(v_prime)
    all_w_fluc.extend(w_prime)

# Convert arrays to numpy blocks
z_coords = np.array(all_z_positions)
u_p = np.array(all_u_fluc)
v_p = np.array(all_v_fluc)
w_p = np.array(all_w_fluc)

# --- 2. Spatial Binning along the Flotation Column Height (Z) ---
num_bins = 150
z_bins = np.linspace(-10, 10, num_bins + 1)
bin_centers = 0.5 * (z_bins[:-1] + z_bins[1:])

reynolds_uw = np.zeros(num_bins)
reynolds_vw = np.zeros(num_bins)

for i in range(num_bins):
    mask = (z_coords >= z_bins[i]) & (z_coords < z_bins[i+1])
    if np.sum(mask) > 0:
        reynolds_uw[i] = np.mean(u_p[mask] * w_p[mask])
        reynolds_vw[i] = np.mean(v_p[mask] * w_p[mask])

# --- 3. Plotting the Reynolds Stress Profiles (Swapped Axes) ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

# Top Plot: X-Z Shear stress profile
ax1.plot(bin_centers, reynolds_uw, color='crimson', marker='o', lw=1.5, label=r'$\langle u^\prime w^\prime \rangle$')
ax1.axhline(0, color='black', linestyle=':', alpha=0.5)
ax1.set_ylabel(r'Reynolds Stress $\langle u^\prime w^\prime \rangle$ (m$^2$/s$^2$)')
ax1.grid(True, linestyle='--', alpha=0.4)
ax1.legend(loc='upper right', fontsize=12)

# Bottom Plot: Y-Z Shear stress profile
ax2.plot(bin_centers, reynolds_vw, color='darkturquoise', marker='s', lw=1.5, label=r'$\langle v^\prime w^\prime \rangle$')
ax2.axhline(0, color='black', linestyle=':', alpha=0.5)
ax2.set_xlabel(r'Flotation Column Height, $Z$ (mm)')
ax2.set_ylabel(r'Reynolds Stress $\langle v^\prime w^\prime \rangle$ (m$^2$/s$^2$)')
ax2.grid(True, linestyle='--', alpha=0.4)
ax2.legend(loc='upper right', fontsize=12)

#plt.suptitle(r'\textbf{Kinetic Particle Reynolds Shear Stresses along Flotation Column}', fontsize=14, y=0.96)
plt.tight_layout()
plt.show()
