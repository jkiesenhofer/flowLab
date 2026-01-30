import numpy as np
import matplotlib.pyplot as plt
import random
# Gitter
nx, ny = 64, 64
Lx, Ly = 1.0, 1.0
dx = Lx / nx
dy = Ly / ny

# Zeit
dt = 0.001
nt = 1000

# Parameter
nu = 0.01  # Viskosität
rho = 1000
# Felder
u = np.zeros((nx, ny))
v = np.zeros((nx, ny))
p = np.zeros((nx, ny))

def laplacian(f):
    return (
        (np.roll(f, 1, axis=0) - 2*f + np.roll(f, -1, axis=0)) / dx**2 +
        (np.roll(f, 1, axis=1) - 2*f + np.roll(f, -1, axis=1)) / dy**2
    )

def divergence(u, v):
    return (
        (np.roll(u, -1, axis=0) - np.roll(u, 1, axis=0)) / (2*dx) +
        (np.roll(v, -1, axis=1) - np.roll(v, 1, axis=1)) / (2*dy)
    )

def pressure_poisson(p, rhs, iters=50):
    for _ in range(iters):
        p = (
            (np.roll(p, 1, axis=0) + np.roll(p, -1, axis=0)) * dy**2 +
            (np.roll(p, 1, axis=1) + np.roll(p, -1, axis=1)) * dx**2 -
            rhs * dx**2 * dy**2
        ) / (2 * (dx**2 + dy**2))
    return p

# Anfangsstörung
u[30:34, 30:34] = random.random()

for n in range(nt):
    u_star = u + dt * (
        -u * (np.roll(u, -1, axis=0) - u) / dx
        -v * (np.roll(u, -1, axis=1) - u) / dy
        + nu * laplacian(u)
    )

    v_star = v + dt * (
        -u * (np.roll(v, -1, axis=0) - v) / dx
        -v * (np.roll(v, -1, axis=1) - v) / dy
        + nu * laplacian(v)
    )

    rhs = divergence(u_star, v_star) / dt
    p = pressure_poisson(p, rhs)

    u = u_star - dt * (np.roll(p, -1, axis=0) - p) / dx
    v = v_star - dt * (np.roll(p, -1, axis=1) - p) / dy


speed = np.transpose(np.sqrt(u**2 + v**2))
compressibility=divergence(u,v)

x = np.linspace(0, Lx, nx)
y = np.linspace(0, Ly, ny)
X, Y = np.meshgrid(x, y)
Re=rho * speed.T * Lx / nu;
plt.figure(figsize=(6, 5))
contour = plt.contourf(X, Y, p)
plt.colorbar(contour, label="p")
plt.xlabel("x")
plt.ylabel("y")
plt.tight_layout()
plt.show()
