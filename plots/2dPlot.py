import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np


# Enable LaTeX-style fonts
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 16
})

def plot_vtk_capillary_fitted(file_path):
    # 1. Load the VTK file
    try:
        mesh = pv.read(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 2. Check for 'capillaryNumber'
    if 'capillaryNumber' not in mesh.array_names:
        print(f"Array 'capillaryNumber' not found. Available: {mesh.array_names}")
        return

    # 3. Convert Cell Data to Point Data
    if 'capillaryNumber' in mesh.cell_data:
        mesh = mesh.cell_data_to_point_data()

    # 4. Slice for 2D (XY Plane)
    z_mid = (mesh.bounds[4] + mesh.bounds[5]) / 2
    slice_mesh = mesh.slice(normal='z', origin=(0, 0, z_mid))

    # 5. Extract data
    x = slice_mesh.points[:, 0]
    y = slice_mesh.points[:, 1]
    capillary_values = slice_mesh['capillaryNumber']

    # 6. Create the plot
    plt.figure(figsize=(12, 7))
    
    # Scale limits
    v_min, v_max = 0, 1.8550261e-05
    levels = np.linspace(v_min, v_max, 100)
    
    plot = plt.tricontourf(x, y, capillary_values, 
                           levels=levels, 
                           vmin=v_min, 
                           vmax=v_max, 
                           cmap='viridis', 
                           extend='both')
    
    # Add styling
    plt.colorbar(plot, label='Capillary Number (Ca)')
    plt.title('Capillary Number Distribution (Fitted View)')
    
    # --- ADJUST LIMITS TO DATA ---
    # This ensures the plot "hugs" the edges of your data
    plt.xlim(np.min(x), np.max(x))
    plt.ylim(np.min(y), np.max(y))
    
    # Keep aspect ratio equal so geometry isn't distorted
    plt.gca().set_aspect('equal', adjustable='box')
    
    # --- GRID OFF ---
    plt.grid(False)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_vtk_capillary_fitted('attachment.vtk')
