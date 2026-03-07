#include <cmath>

// Particle structure
struct Particle {
    double x, y;      // position
    double vx, vy;    // velocity
    double mass;
    double radius;
};

// Compute distance between two particles
inline double distance(const Particle &a, const Particle &b) {
    return std::sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y));
}

// Resolve elastic collision between two particles
inline void resolveCollision(Particle &a, Particle &b) {
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    double dist = std::sqrt(dx*dx + dy*dy);

    if (dist == 0) return; // avoid division by zero

    double nx = dx / dist;
    double ny = dy / dist;

    double dvx = a.vx - b.vx;
    double dvy = a.vy - b.vy;

    double relVel = dvx*nx + dvy*ny;

    if (relVel > 0) return; // moving apart

    double e = 1.0; // restitution (1 = perfectly elastic)
    double j = -(1 + e) * relVel;
    j /= (1/a.mass + 1/b.mass);

    double impulseX = j * nx;
    double impulseY = j * ny;

    a.vx += impulseX / a.mass;
    a.vy += impulseY / a.mass;

    b.vx -= impulseX / b.mass;
    b.vy -= impulseY / b.mass;
}
