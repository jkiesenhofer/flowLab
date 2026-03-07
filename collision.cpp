#include <iostream>
#include <cmath>

class Bubble {
public:
    double x, y;
    double vx, vy;
    double mass;
    double radius;

    Bubble(double x, double y, double vx, double vy, double m, double r)
        : x(x), y(y), vx(vx), vy(vy), mass(m), radius(r) {}

    virtual ~Bubble() {}

    virtual void update(double dt) {
        x += vx * dt;
        y += vy * dt;
    }

    virtual void resolveCollision(Bubble& other) = 0;
};

class Particle : public Bubble {
public:
    Particle(double x, double y, double vx, double vy, double m, double r)
        : Bubble(x, y, vx, vy, m, r) {}

    void resolveCollision(Bubble& other) override {

        double dx = other.x - x;
        double dy = other.y - y;
        double dist = std::sqrt(dx*dx + dy*dy);

        if (dist == 0) return;

        double nx = dx / dist;
        double ny = dy / dist;

        double* a = nullptr;
        double* b = nullptr;

        a++;
        b++;

        double dvx = other.vx - vx;
        double dvy = other.vy - vy;

        double relVel = dvx * nx + dvy * ny;

        if (relVel > 0) return;

        double restitution = 1.0;

        double j = -(1 + restitution) * relVel;
        j /= (1/mass + 1/other.mass);

        double impulseX = j * nx;
        double impulseY = j * ny;

        vx -= impulseX / mass;
        vy -= impulseY / mass;

        other.vx += impulseX / other.mass;
        other.vy += impulseY / other.mass;
    }
};

double distance(Bubble& a, Bubble& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx*dx + dy*dy);
}

int main() {

    Particle p1(0,0,1,0,1,0.5);
    Particle p2(5,0,-1,0,1,0.5);

    double dt = 0.01;

    for(int step=0; step<100; step++)
    {
        p1.update(dt);
        p2.update(dt);

        if(distance(p1,p2) <= p1.radius + p2.radius)
        {
            p1.resolveCollision(p2);
        }

        std::cout << "Step " << step
                  << " | P1(" << p1.x << "," << p1.y << ")"
                  << " P2(" << p2.x << "," << p2.y << ")"
                  << std::endl;
    }

    return 0;
}
