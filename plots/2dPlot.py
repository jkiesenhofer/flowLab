import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np

def plot_vtk_weber_range(file_path):
    # 1. Load the VTK file
    try:
        mesh = pv.read(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 2. Check for 'weberNumber'
    if 'weberNumber' not in mesh.array_names:
        print(f"Array 'weberNumber' not found. Available: {mesh.array_names}")
        return

    # 3. Convert Cell Data to Point Data to avoid dimension mismatch
    if 'weberNumber' in mesh.cell_data:
        mesh = mesh.cell_data_to_point_data()

    # 4. Slice for 2D (XY Plane)
    z_mid = (mesh.bounds[4] + mesh.bounds[5]) / 2
    slice_mesh = mesh.slice(normal='z', origin=(0, 0, z_mid))

    # 5. Extract data
    x = slice_mesh.points[:, 0]
    y = slice_mesh.points[:, 1]
    weber_values = slice_mesh['weberNumber']

    # 6. Create the plot with fixed color limits
    plt.figure(figsize=(12, 7))
    
    # vmin and vmax set the scale range
    # np.linspace ensures the contour levels are strictly within your 30-50 range
    levels = np.linspace(0, 5, 100)
    
    plot = plt.tricontourf(x, y, weber_values, 
                           levels=levels, 
                           vmin=0, 
                           vmax=5, 
                           cmap='viridis', 
                           extend='both') # 'extend' adds arrows to colorbar for out-of-range values
    
    # Add styling
    cb = plt.colorbar(plot, label='Weber Number (We)')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Weber Number Distribution (Range: 30 - 50)')
    plt.axis('equal')
    plt.grid(False)
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_vtk_weber_range('attachment.vtk')
