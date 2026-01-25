import random
import math
import matplotlib.pyplot as plt

# Parameter
n = 200           # Anzahl Teilchen
width = 20        # Breite des Bereichs
min_dist = 0.5    # Mindestabstand
max_height = 0.1   # maximale Start-Höhe

# Liste der Punkte
points = []

# Hilfsfunktion: Prüft, ob neuer Punkt Mindestabstand zu allen anderen hat
def is_valid(new_point, points, min_dist):
    return all(math.dist(new_point, p) >= min_dist for p in points)

# Punkte „fallen lassen“
for i in range(n):
    # Zufällige x-Position
    x = random.uniform(0, width)
    y = max_height
    
    # Fallen lassen, bis Mindestabstand erreicht ist
    while True:
        collision = False
        for px, py in points:
            if math.dist((x, y), (px, py)) < min_dist:
                collision = True
                y = py + min_dist  # auf Punkt „stapeln“
        if not collision:
            break
    points.append((x, y))

# Scatter-Plot
x_vals = [p[0] for p in points]
y_vals = [p[1] for p in points]

plt.figure(figsize=(8,6))
plt.scatter(x_vals, y_vals, c="blue", s=50)
plt.title("Dispersed metal particles in air")
plt.xlim(0, width)
plt.ylim(0, max(y_vals)+1)
plt.gca().set_aspect("equal", adjustable="box")
plt.grid(True, linestyle="--", alpha=0.4)

# Bild speichern
plt.savefig('point_cloud.png', dpi=300)

