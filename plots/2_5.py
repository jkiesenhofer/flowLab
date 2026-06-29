import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc

# Set up the figure with 3 subplots side-by-side
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)

# Configuration parameters
R = 0.6  # Particle radius
z_values = [-0.22, 0.0, 0.22]  # Center positions for each case
titles_theta = [r'$\theta > 90^\circ$', r'$\theta = 90^\circ$', r'$\theta < 90^\circ$']
titles_z = [r'$z < 0$', r'$z = 0$', r'$z > 0$']

for i, (ax, z, t_theta, t_z) in enumerate(zip(axes, z_values, titles_theta, titles_z)):
    # 1. Fill the phases (Air on top, Water on bottom)
    ax.axhspan(0, 1.2, facecolor='#ffffff', edgecolor='none')  # Air (White)
    ax.axhspan(-1.2, 0, facecolor='#a3daff', alpha=0.7, edgecolor='none')  # Water (Light Blue)
    
    # 2. Draw the main three-phase interface line
    ax.axhline(0, color='black', linewidth=1.5, zorder=2)
    
    # Define particle center
    cx, cy = 0.0, z
    
    # Calculate contact point at the right side of the interface (y = 0)
    contact_x = cx + np.sqrt(R**2 - z**2)
    contact_y = 0.0
    
    # 3. Draw the particle
    particle = plt.Circle((cx, cy), R, facecolor='none', edgecolor='black', linewidth=2.5, zorder=4)
    ax.add_patch(particle)
    
    # 4. Draw center of mass dot and its vector z
    ax.plot(cx, cy, 'ko', markersize=4, zorder=5)
    if z != 0:
        ax.arrow(cx, 0, 0, z, head_width=0.03, head_length=0.04, fc='black', ec='black', length_includes_head=True, zorder=5)
    
    # 5. Interfacial tension vectors
    # Surface tension of water-air (sigma_0)
    ax.arrow(contact_x, contact_y, 0.28, 0, head_width=0.03, head_length=0.04, fc='black', ec='black', zorder=5)
    ax.text(contact_x + 0.15, -0.15, r'$\sigma_0$', fontsize=12)
    
    # Calculate tangent angles
    phi = np.arctan2(contact_y - cy, contact_x - cx)
    
    # Tangent vector pointing up into the Air phase (gamma_p,a)
    gamma_pa_angle = phi + np.pi/2
    dx_pa = 0.28 * np.cos(gamma_pa_angle)
    dy_pa = 0.28 * np.sin(gamma_pa_angle)
    ax.arrow(contact_x, contact_y, dx_pa, dy_pa, head_width=0.03, head_length=0.04, fc='black', ec='black', zorder=5)
    
    # Positioned gamma_p,a higher: adjusted dy text offset from +0.02 to +0.08
    ax.text(contact_x + dx_pa + 0.02, contact_y + dy_pa + 0.08, r'$\gamma_{p,a}$', fontsize=12, ha='center', va='bottom')
    
    # Tangent vector pointing down into the Water phase (gamma_p,w)
    gamma_pw_angle = phi - np.pi/2
    dx_pw = 0.28 * np.cos(gamma_pw_angle)
    dy_pw = 0.28 * np.sin(gamma_pw_angle)
    ax.arrow(contact_x, contact_y, dx_pw, dy_pw, head_width=0.03, head_length=0.04, fc='black', ec='black', zorder=5)
    ax.text(contact_x + dx_pw + 0.02, contact_y + dy_pw - 0.1, r'$\gamma_{p,w}$', fontsize=12, ha='center')
    
    # 6. Draw the Contact Angle Arc (theta)
    theta_deg = np.degrees(gamma_pa_angle)
    arc = Arc((contact_x, contact_y), 0.25, 0.25, angle=0, theta1=0, theta2=theta_deg, color='black', linewidth=2, zorder=5)
    ax.add_patch(arc)
    
    # Label the angle theta
    text_angle = np.radians(theta_deg / 2)
    ax.text(contact_x + 0.2 * np.cos(text_angle), contact_y + 0.18 * np.sin(text_angle), t_theta, fontsize=12, va='bottom')
    
    # 7. Labels inside the panels
    ax.text(-0.85, 1.05, 'AIR', fontsize=14, fontweight='bold', ha='left', va='top')
    ax.text(-0.85, -1.05, 'WATER', fontsize=14, fontweight='bold', ha='left', va='bottom')
    ax.text(-0.35, cy + (0.05 if z >= 0 else -0.1), t_z, fontsize=12)
    
    # Panel layout boundaries and styling
    ax.set_xlim(-0.95, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect('equal')
    
    # Draw border outline around each subplot box
    for spine in ax.spines.values():
        spine.set_edgecolor('#b5b5b5')
        spine.set_linewidth(1.5)
        
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

plt.tight_layout()
plt.show()
