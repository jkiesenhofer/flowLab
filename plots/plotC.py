import re
import matplotlib.pyplot as plt

def plot_reynolds_number(file_path):
    re_values = []
    
    # Regular expression to find the float after the specific string
    # Matches 'Average Reynolds Number: ' followed by an integer or float
    pattern = re.compile(r"Average Reynolds Number:\s+([-+]?\d*\.\d+|\d+)")

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    # Convert the captured group to a float
                    re_values.append(float(match.group(1)))
        
        if not re_values:
            print(f"No matches found in {file_path}. Check the string format.")
            return

        # Plotting the data
        plt.figure(figsize=(10, 6))
        plt.plot(re_values, marker='o', linestyle='-', color='b', markersize=4)
        
        plt.title('Average Reynolds Number Over Time', fontsize=14)
        plt.xlabel('Iteration / Time Step', fontsize=12)
        plt.ylabel('Average Reynolds Number', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")

if __name__ == "__main__":
    # Ensure 'log.tpyFoam' is in the same directory as this script
    plot_reynolds_number('log.tpcFoam')
