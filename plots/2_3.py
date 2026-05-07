import matplotlib.pyplot as plt
import numpy as np

# 1. Plot Styling
plt.rcParams.update({
    "font.family": "serif",
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "axes.titlesize": 18,
    "grid.alpha": 0.3
})

# 2. Data Generation
# Reynolds number range (Logarithmic)
re_numbers = np.logspace(1, 4, 500) 

# Empirical model for Strouhal Number (St) vs Re for a bubble/sphere
# Formula: St = 0.21 * (1 - 21/Re)
st_numbers = 0.21 * (1 - 21/re_numbers)

# Hide values below the critical Re where periodic shedding typically starts
st_numbers[re_numbers < 21] = np.nan

# 3. Visualization
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the primary curve
ax.loglog(re_numbers, st_numbers, label=r'1mm Bubble Approximation', color='dodgerblue', lw=2.5)

# Add asymptotic reference line at St = 0.21
ax.axhline(y=0.21, color='crimson', linestyle='--', alpha=0.8, label=r'Asymptotic Limit ($St \approx 0.21$)')

# Formatting labels and title
ax.set_title(r'Strouhal Number ($St$) vs. Reynolds Number ($Re$)', pad=20)
ax.set_xlabel(r'Reynolds Number ($Re$)', labelpad=10)
ax.set_ylabel(r'Strouhal Number ($St$)', labelpad=10)

# Grid and Legend
ax.grid(True, which="both", ls="-")
ax.legend(frameon=True, loc='lower right', fontsize=12)

plt.tight_layout()
plt.show()
