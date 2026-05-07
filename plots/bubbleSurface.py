import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def simulate_dimple():
    # --- Parameters ---
    b_radius = 1.2      # Radius of the bubble
    p_radius = 0.7      # Radius of the rigid particle
    b_center = np.array([0, 0, 0])     # Bubble at origin
    p_center = np.array([0, 0, 1.3])   # Particle pressing from above
    
    res = 70  # Mesh resolution
    u = np.linspace(0, 2 * np.pi, res)
    v = np.linspace(0, np.pi, res)
    
    # --- Generate Bubble Surface ---
    # We use meshgrid for easier coordinate manipulation
    U, V = np.meshgrid(u, v)
    bx = b_radius * np.cos(U) * np.sin(V) + b_center[0]
    by = b_radius * np.sin(U) * np.sin(V) + b_center[1]
    bz = b_radius * np.cos(V) + b_center[2]

    # --- Apply Deformation (The "Press") ---
    # We iterate through the surface and check for overlap with the particle
    for i in range(res):
        for j in range(res):
            # Current point on the bubble surface
            point = np.array([bx[i,j], by[i,j], bz[i,j]])
            
            # Vector from particle center to the bubble point
            vec_p_to_b = point - p_center
            dist_to_p = np.linalg.norm(vec_p_to_b)
            
            # If the point is inside the particle, push it to the particle's surface
            if dist_to_p < p_radius:
                # Direction to push the bubble surface
                direction = vec_p_to_b / dist_to_p
                # Snap the point to the surface of the rigid sphere
                new_point = p_center + direction * p_radius
                bx[i,j], by[i,j], bz[i,j] = new_point

    # --- Generate Rigid Particle Mesh ---
    pu = np.linspace(0, 2 * np.pi, 30)
    pv = np.linspace(0, np.pi, 30)
    px = p_radius * np.outer(np.cos(pu), np.sin(pv)) + p_center[0]
    py = p_radius * np.outer(np.sin(pu), np.sin(pv)) + p_center[1]
    pz = p_radius * np.outer(np.ones(np.size(pu)), np.cos(pv)) + p_center[2]

    # --- Visualization ---
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the deformed Bubble (the "pushed" surface)
    bubble_surf = ax.plot_surface(bx, by, bz, color='skyblue', alpha=0.6, 
                                  edgecolor='navy', linewidth=0.1, antialiased=True)


    # Lighting and view
    ax.view_init(elev=20, azim=45)
    ax.set_title("Particle Pressing into Bubble Surface", fontsize=15)
    
    # Equalize axes
    max_range = np.array([bx.max()-bx.min(), by.max()-by.min(), bz.max()-bz.min()]).max() / 2.0
    mid_x = (bx.max()+bx.min()) * 0.5
    mid_y = (by.max()+by.min()) * 0.5
    mid_z = (bz.max()+bz.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.show()

if __name__ == "__main__":
    simulate_dimple()
