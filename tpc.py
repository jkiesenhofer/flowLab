import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parameters of asymmetric monopoles
# -----------------------------
# Each monopole has a strength Q and a position (x, y)
monopole1 = {"Q": 1.0, "pos": (-1.0, -1.0)}
monopole2 = {"Q": -0.5, "pos": (1.0, 1.5)}

# -----------------------------
# Create computational grid
# -----------------------------
x = np.linspace(-3, 3, 300)
y = np.linspace(-2, 2, 200)
X, Y = np.meshgrid(x, y)

# -----------------------------
# Function for a point source (monopole)
# -----------------------------
def potential_monopole(Q, x0, y0, X, Y):
    """Velocity potential of a monopole at (x0, y0) with strength Q"""
    return Q / (4 * np.pi) * np.log(np.sqrt((X - x0)**2 + (Y - y0)**2))

# -----------------------------
# Compute potential fields
# -----------------------------
phi_total = potential_monopole(monopole1["Q"], monopole1["pos"][0], monopole1["pos"][1], X, Y)
phi_total += potential_monopole(monopole2["Q"], monopole2["pos"][0], monopole2["pos"][1], X, Y)

# -----------------------------
# Create contour plot
# -----------------------------
plt.figure(figsize=(10, 6))
contours = plt.contour(X, Y, phi_total, levels=50, cmap='plasma')
plt.clabel(contours, inline=True, fontsize=8)
plt.title("Contour Plot of Two Asymmetric Monopoles")
plt.xlabel("x")
plt.ylabel("y")
plt.scatter([monopole1["pos"][0], monopole2["pos"][0]],
            [monopole1["pos"][1], monopole2["pos"][1]])
plt.legend()
plt.axis("equal")
plt.show()
