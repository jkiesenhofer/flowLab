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

# Storage arrays to track positions and dissipation across all space and time
all_z_positions = []
all_dissipation = []

# --- 1. Run Simulation and Compute Dissipation Rate ---
for step in range(NUM_STEPS):
    noise_p = np.random.normal(0, 1, (NUM_PARTICLES, 3))
    
    # Kinematics Update
    particle_vel += (-particle_vel / TAU_PARTICLE) * DT + (TURB_INTENSITY_PARTICLE * np.sqrt(DT) * noise_p)
    particle_pos += particle_vel * DT
    
    # Calculate spatial mean flow profile at this instant
    mean_u = np.mean(particle_vel[:, 0])
    mean_v = np.mean(particle_vel[:, 1])
    mean_w = np.mean(particle_vel[:, 2])
    
    # Fluctuations from the mean flow field (u', v', w')
    u_prime = particle_vel[:, 0] - mean_u
    v_prime = particle_vel[:, 1] - mean_v
    w_prime = particle_vel[:, 2] - mean_w
    
    # Turbulent Kinetic Energy Dissipation rate per particle: epsilon = (u'^2 + v'^2 + w'^2) / tau_p
    epsilon_p = (u_prime**2 + v_prime**2 + w_prime**2) / TAU_PARTICLE
    
    # Convert Z positions to millimeters and log properties
    all_z_positions.extend(particle_pos[:, 2] * 1000)
    all_dissipation.extend(epsilon_p)

# Convert tracked parameters to numpy blocks
z_coords = np.array(all_z_positions)
dissipation = np.array(all_dissipation)

# --- 2. Spatial Binning along the Flotation Column Height (Z) ---
num_bins = 150
z_bins = np.linspace(-10, 10, num_bins + 1)
bin_centers = 0.5 * (z_bins[:-1] + z_bins[1:])

mean_dissipation_profile = np.zeros(num_bins)

for i in range(num_bins):
    mask = (z_coords >= z_bins[i]) & (z_coords < z_bins[i+1])
    if np.sum(mask) > 0:
        # Compute ensemble average dissipation rate inside this height slice
        mean_dissipation_profile[i] = np.mean(dissipation[mask])

# --- 3. Plotting the Turbulent Energy Dissipation Rate Profile ---
plt.figure(figsize=(9, 5.5))

plt.plot(bin_centers, mean_dissipation_profile, color='forestgreen', lw=1.5, label=r'$\langle \varepsilon \rangle$')
plt.axhline(np.mean(dissipation), color='black', linestyle=':', alpha=0.6, label='Global Average Dissipation')

# Labeling and Grid Configuration
plt.xlabel(r'Flotation Column Height, $Z$ (mm)')
plt.ylabel(r'Turbulent Energy Dissipation Rate, $\langle \varepsilon \rangle$ (m$^2$/s$^3$)')
#plt.title(r'\textbf{Spatial Turbulent Dissipation Rate Profile along Flotation Column}', fontsize=14, pad=15)
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.show()
