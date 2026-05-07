import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

def generate_acting_forces_simulation():
    # --- 1. Simulation Parameters ---
    b_radius = 1.2          # Radius of the bubble
    p_radius = 0.7          # Radius of the rigid particle
    steps = 100             # Time resolution
    time = np.linspace(0, 10, steps)
    
    # Particle movement: starts just above contact (1.9) and indents to 1.1
    p_z_positions = np.linspace(b_radius + p_radius, 1.1, steps)

    # Physical Constants (Simulated scaling factors)
    k_surface = 5.0         # Spring constant for contact resistance
    gamma = 2.0             # Surface tension coefficient
    P0 = 1.0                # Internal pressure factor

    # Mesh resolution for calculations
    res = 40
    u = np.linspace(0, 2 * np.pi, res)
    v = np.linspace(0, np.pi, res)
    U, V = np.meshgrid(u, v)
    
    # Original undeformed bubble coordinates
    bx_orig = b_radius * np.cos(U) * np.sin(V)
    by_orig = b_radius * np.sin(U) * np.sin(V)
    bz_orig = b_radius * np.cos(V)

    # Storage for force histories
    contact_forces = []
    surface_tension_forces = []
    pressure_resistance = []

    # --- 2. Dynamic Calculation Loop ---
    for z_pos in p_z_positions:
        p_center = np.array([0, 0, z_pos])
        
        # Calculate distance from particle center to bubble surface points
        dx = bx_orig - p_center[0]
        dy = by_orig - p_center[1]
        dz = bz_orig - p_center[2]
        dist_to_p = np.sqrt(dx**2 + dy**2 + dz**2)
        
        # Identify area of contact
        mask = dist_to_p < p_radius
        
        if np.any(mask):
            # A. Contact Force: Proportional to total vertical displacement (indentation depth)
            displacements = p_radius - dist_to_p[mask]
            f_contact = np.sum(displacements) * k_surface / 100.0
            
            # B. Surface Tension Resistance: Proportional to change in surface area
            # We calculate a proxy based on the stretching of the surface coordinates
            bz_new = bz_orig.copy()
            bz_new[mask] = p_center[2] + (dz[mask] / dist_to_p[mask]) * p_radius
            new_dist = np.sqrt(bx_orig**2 + by_orig**2 + bz_new**2)
            total_stretch = np.sum(new_dist - b_radius)
            f_st = total_stretch * gamma / 50.0
            
            # C. Internal Pressure: Proportional to the volume of the dimple
            # Simplified as the integral of indentation over the mask area
            vol_proxy = np.sum(displacements) * (p_radius / res)
            f_pres = vol_proxy * P0 / 5.0
        else:
            f_contact = 0.0
            f_st = 0.0
            f_pres = 0.0
            
        contact_forces.append(f_contact)
        surface_tension_forces.append(f_st)
        pressure_resistance.append(f_pres)

    # --- 3. Plotting the Acting Forces ---
    plt.figure(figsize=(10, 6))
    
    plt.plot(time, contact_forces, label='Contact Force', color='blue', linewidth=2.5)
    plt.plot(time, surface_tension_forces, label='Surface Tension', color='green', linestyle='--')
    plt.plot(time, pressure_resistance, label='Internal Pressure', color='red', linestyle=':')
    
    # Fill under the main force for visual emphasis
    plt.fill_between(time, contact_forces, alpha=0.1, color='blue')
    
    plt.title('Acting Forces: Particle-Bubble Interaction', fontsize=16)
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Force Magnitude (N)', fontsize=14)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend(loc='upper left', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('acting_forces_chart.png')
    plt.show()

if __name__ == "__main__":
    generate_acting_forces_simulation()
