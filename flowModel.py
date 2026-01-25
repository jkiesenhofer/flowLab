import random
import math
import matplotlib.pyplot as plt

# Parameter
n = 920          # Number of particles
width = 80       # Width of the area
min_dist = 2.2   # Minimum distance
max_height = 0   # Maximum starting height

# List of Lagrangian particles
points = []

# Auxiliary function: Checks whether new point has minimum distance to all others
def is_valid(new_point, points, min_dist):
    return all(math.dist(new_point, p) >= min_dist for p in points)

# Drop points
for i in range(n):
    # Random x-position
    x = random.uniform(0, width)
    y = max_height
    
    # Drop until minimum distance is reached
    while True:
        collision = False
        for px, py in points:
            if math.dist((x, y), (px, py)) < min_dist:
                collision = True
                y = py + min_dist  # “stack” on point
        if not collision:
            break
    points.append((x, y))

# Scatter-Plot
x_vals = [p[0] for p in points]
y_vals = [p[1] for p in points]

plt.figure(figsize=(8,6))
plt.scatter(x_vals, y_vals, c="blue", s=20)
plt.title("Dispersed metal particles in air")
plt.xlim(0, width)
plt.ylim(max_height, max(y_vals)+1)
plt.gca().set_aspect("equal", adjustable="box")
plt.grid(True, linestyle="--", alpha=0.4)

# Save image
plt.savefig('flowModel.png', dpi=300)
