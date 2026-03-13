import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
df = pd.read_csv("OF/flotation_10/data.csv")

# Compute mean
mean_val = df["p_rgh"].mean()
''''
# Plot histogram
plt.hist(df["p_rgh"].sort_values())

# Add mean line
plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Mean = {mean_val:.2f}')
'''

x = df["Cell ID"]
y = df["U.water_Magnitude"]

coeffs = np.polyfit(x, y, deg=3)  # deg=1 für linear
a, c, m, b = coeffs
print(f"Lineare Funktion: y = {m:.2f}*x + {b:.2f}")

# Fit-Linie für Plot erstellen
y_fit = m * x + b + c * x**2 + a*x**3
plt.scatter(x,y, marker='.')
plt.plot(x, y_fit, color='red', label='Ausgleichsfunktion')
# Lineares Fit: y = m*x + b

# Labels and title using LaTeX
plt.xlabel(r"\textbf{Cell ID}")
plt.ylabel(r"\textbf{$U_f$}")
plt.title(r"\textbf{Hydrostatic pressure contribution}")

# Rotate x-ticks for readability
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()
plt.show()
