import matplotlib.pyplot as plt
import numpy as np

# Set up the figure style to match the classic Zisman plot look
plt.figure(figsize=(8, 9))

# Surface tension values (mN/m) of testing liquids
gamma_l = np.array([30, 40, 50, 60, 70, 75])

# Synthetic data parameters for bioplastics and lipids
materials = {
    'PLA (Bioplastic)': {
        'slope': -0.018,
        'intercept': 1.35,
        'marker': 'o',
    },
    'PHB (Bioplastic)': {
        'slope': -0.022,
        'intercept': 1.48,
        'marker': 's',
    },
    'Lecithin (Lipid)': {
        'slope': -0.025,
        'intercept': 1.60,
        'marker': '^',
    },
    'Triolein (Lipid)': {
        'slope': -0.030,
        'intercept': 1.75,
        'marker': 'd',
    },
    'Cholesterol (Lipid)': {
        'slope': -0.015,
        'intercept': 1.20,
        'marker': 'v',
    },
}

# Plotting each material's trendline and data points
for name, props in materials.items():
  # Calculate cosine of contact angle and cap at 1.0 (complete wetting region)
  cos_theta = props['slope'] * gamma_l + props['intercept']
  cos_theta = np.clip(cos_theta, 0.0, 1.0)

  # Linear regression line for points below complete wetting
  valid_idx = cos_theta < 1.0
  if np.any(valid_idx):
    x_fit = gamma_l[valid_idx]
    y_fit = cos_theta[valid_idx]
    m, b = np.polyfit(x_fit, y_fit, 1)

    # Generate trend line across the plot frame
    x_line = np.linspace(25, 78, 100)
    y_line = m * x_line + b
    y_line = np.clip(y_line, 0.0, 1.0)

    # Plot solid trend line and data markers
    plt.plot(x_line, y_line, 'k-', linewidth=1.5)
    plt.scatter(
        gamma_l,
        cos_theta,
        facecolors='none',
        edgecolors='k',
        marker=props['marker'],
        s=50,
        label=name,
    )

# Formatting the plot to match classic scientific publications
plt.axhline(y=1.0, color='k', linestyle='--', linewidth=1)
plt.xlim(25, 78)
plt.ylim(-0.05, 1.05)

plt.xlabel('Surface Tension (mN/m)', fontsize=13, fontweight='bold')
plt.ylabel('Cosine \u0398', fontsize=13, fontweight='bold')

plt.legend(loc='lower left', frameon=False, fontsize=11)
plt.title(
    'Zisman Plots of Bioplastics and Lipids (Synthetic Data)',
    fontsize=13,
    pad=15,
)

# Clean borders and grid box style
plt.gca().spines['top'].set_linewidth(1)
plt.gca().spines['right'].set_linewidth(1)
plt.gca().spines['bottom'].set_linewidth(1)
plt.gca().spines['left'].set_linewidth(1)

plt.tight_layout()
plt.show()
