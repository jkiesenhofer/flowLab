import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -------------------------
# Parameter
# -------------------------
Nx, Ny = 150, 150
dx = 1.0
dt = 0.01
epsilon = 1.5
steps = 2000

# -------------------------
# Grid & Ab-initio
# -------------------------
phi = 0.05 * np.random.randn(Nx, Ny)

# Laplace-Operator (periodische RB)
def laplace(f):
    return (
        np.roll(f, 1, axis=0) +
        np.roll(f, -1, axis=0) +
        np.roll(f, 1, axis=1) +
        np.roll(f, -1, axis=1) -
        4 * f
    ) / dx**2

# -------------------------
# Time step
# -------------------------
def step(phi):
    mu = phi**3 - phi - epsilon**2 * laplace(phi)
    phi += dt * laplace(mu)
    return phi

# -------------------------
# Plot
# -------------------------
fig, ax = plt.subplots()
im = ax.imshow(phi, cmap="RdBu", vmin=-1, vmax=1)
ax.set_title("2D Two-Phase flow (phase-field)")
plt.colorbar(im)

def update(frame):
    global phi
    for _ in range(5):  # mehrere Schritte pro Frame
        phi = step(phi)
    im.set_data(phi)
    return im,

ani = FuncAnimation(fig, update, frames=300, interval=50)
plt.show()

