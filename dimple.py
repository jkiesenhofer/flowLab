import numpy as np
import matplotlib.pyplot as plt

# --- Geometric Parameters ---
r_bubble = 0.35      # Base bubble radius (mm)
r_particle = 0.15    # Particle radius (mm)
theta = np.linspace(0, 2 * np.pi, 600)
cos_theta = np.cos(theta)

# Define Legendre polynomials for macro-deformation
def p2(x): return 0.5 * (3 * x**2 - 1)
def p3(x): return 0.5 * (5 * x**3 - 3 * x)

# --- Define Time Steps ---
timesteps = [0.0, 0.55, 0.90]
titles = ["Initial State\nt = 0%", 
          "Early Interaction Phase\nt = 55%", 
          "Established Phase\nt = 90%"]

fig, axes = plt.subplots(1, 3, figsize=(15, 6.5))
fig.suptitle('EVOLUTION OF A RISING DIMPLED CAP BUBBLE INTERFACE (Bubble in Water)', fontsize=14, fontweight='bold')

for i, t in enumerate(timesteps):
    ax = axes[i]
    ax.set_facecolor('#edf6f9')  # Clear water blue background
    
    # 1. Macro-deformation (Hydrodynamic drag flattening)
    beta2 = -0.15 * (t / 0.5)  
    beta3 = 0.05 * (t / 0.5)   
    r_base = r_bubble * (1 + beta2 * p2(cos_theta) + beta3 * p3(cos_theta))
    
    # 2. Localized Particle Indentation (Top Dimple at apex)
    indentation_amplitude = 0.32 * (t / 0.5)  
    gaussian_width = 0.45                    
    angle_dist = np.minimum(theta, 2 * np.pi - theta)
    top_dimple = indentation_amplitude * np.exp(- (angle_dist / gaussian_width)**2)
    
    # Final perturbed radius
    r_final = r_base - (r_bubble * top_dimple)
    
    # Convert polar to Cartesian
    x_b = r_final * np.sin(theta)
    y_b = r_final * np.cos(theta)
    
    # 3. Plot Bubble Profile
    ax.plot(x_b, y_b, color='#0077b6', linewidth=2.5, zorder=2)
    ax.fill(x_b, y_b, color='#90e0ef', alpha=0.5, zorder=1)
    
    # 4. Plot Interacting Particle
    particle_y_center = r_final[0] if t == 0 else r_final[0] + 0.02
    particle_circle = plt.Circle((0, particle_y_center), r_particle, 
                                 edgecolor='#3d3d3d', facecolor='#707070', 
                                 linewidth=1.5, zorder=3)
    ax.add_patch(particle_circle)
        
    # 5. Graph Tuning
    ax.set_title(titles[i], fontsize=12, fontweight='bold', pad=12)
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_xlabel('Width (mm)', fontsize=10)
    if i == 0:
        ax.set_ylabel('Height (mm)', fontsize=10)

plt.tight_layout()
plt.show()
