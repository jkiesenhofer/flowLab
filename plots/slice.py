import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np

def plot_capillary_line_graph(file_path):
    # 1. Load the VTK file
    try:
        mesh = pv.read(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 2. Synchronize naming
    if 'weberNumber' in mesh.array_names:
        mesh.rename_array('weberNumber', 'capillaryNumber')
    
    # 3. Define the line for the probe
    # We create a line along the X-axis through the center of Y and Z
    y_mid = (mesh.bounds[2] + mesh.bounds[3]) / 2
    z_mid = (mesh.bounds[4] + mesh.bounds[5]) / 2
    
    point_a = [mesh.bounds[0], y_mid, z_mid] # Start of X
    point_b = [mesh.bounds[1], y_mid, z_mid] # End of X
    
    # 4. Sample the data along the line
    line_probe = mesh.sample_over_line(point_a, point_b, resolution=500)

    # 5. Extract X coordinates and the Capillary values
    x_coords = line_probe.points[:, 0]
    capillary_values = line_probe['capillaryNumber']

    # 6. Plotting the Graph
    plt.figure(figsize=(10, 6))
    plt.plot(x_coords, capillary_values, color='firebrick', linewidth=2, label='Capillary Number')
    
    # Formatting
    plt.title('Capillary Number Profile along X-axis', fontsize=14)
    plt.xlabel('X Position', fontsize=12)
    plt.ylabel('Capillary Number ($Ca$)', fontsize=12)
    
    # Setting your requested Y-limits for the graph values
    plt.ylim(0, 1.8550261e-05)
    
    plt.grid(True, linestyle='--', alpha=0.6) # Grid on for 1D graphs for better readability
    plt.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_capillary_line_graph('attachment.vtk')
