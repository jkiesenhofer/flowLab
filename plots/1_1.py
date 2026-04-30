

import re
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 26
})


def plot_weber_number(file_path):
    weber_values = []
    
    # Matches 'Average Weber Number: ' followed by an integer or float
    pattern = re.compile(r"Average Weber Number:\s+([-+]?\d*\.\d+|\d+)")

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    weber_values.append(float(match.group(1)))
        
        if not weber_values:
            print(f"No matches found in {file_path}. Check the string format.")
            return

        # --- NORMALIZATION LOGIC ---
        # Assuming you want to normalize by the total number of points (0 to 1 scale)
        # Or you can replace 'total_points' with a physical time constant.
        total_points = len(weber_values)
        normalized_time = [i / (total_points - 1) for i in range(total_points)]
        # ---------------------------

        # Plotting the data
        plt.figure(figsize=(10, 6))
        
        # Use normalized_time for the x-axis instead of the default index
        plt.plot(normalized_time, weber_values, marker='o', linestyle='-', color='b', markersize=4)
        
        #plt.title('Average Weber Number vs. Normalized Time', fontsize=14)
        plt.xlabel('$t/t_{end}$', fontsize=20)
        plt.ylabel('$We$', fontsize=20)
        plt.grid(True, linestyle='--', alpha=0.7)

        # Adjusted xlim for a 0-1 normalized scale
        # (If you still want 20-7000, you must normalize those bounds too)
        plt.xlim([0.001, 1])

        plt.ylim([0, 0.1])
        
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")

if __name__ == "__main__":
    plot_weber_number('log.tpcFoam')
