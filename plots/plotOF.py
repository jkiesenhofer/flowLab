import pandas as pd
import matplotlib.pyplot as plt

# Enable LaTeX-style fonts
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.titlesize": 16
})

# Load CSV file
df = pd.read_csv("pointData.csv")

# Compute mean
mean_val = df["velocity_Magnitude"].mean()

# Plot histogram
plt.hist(df["velocity_Magnitude"], bins=16, color="skyblue", edgecolor="black")

# Add mean line
plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Mean = {mean_val:.2f}')

# Labels and title using LaTeX
plt.xlabel(r"\textbf{Velocity Magnitude} (\textit{m/s})")
plt.ylabel(r"\textbf{Incidences}")
plt.title(r"\textbf{Distribution of Velocity Magnitude}")

# Rotate x-ticks for readability
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
