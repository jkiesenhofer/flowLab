#include <iostream>
#include <cmath>

struct Particle {
    double x, y;
    double vx, vy;
    double mass;
    double radius;
};

double distance(Particle &a, Particle &b)
{
    return std::sqrt((a.x-b.x)*(a.x-b.x) + (a.y-b.y)*(a.y-b.y));
}

void resolveCollision(Particle &a, Particle &b)
{
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    double dist = std::sqrt(dx*dx + dy*dy);

    if (dist == 0) return;

    double nx = dx/dist;
    double ny = dy/dist;

    double dvx = a.vx - b.vx;
    double dvy = a.vy - b.vy;

    double relVel = dvx*nx + dvy*ny;

    if (relVel > 0) return;

    double e = 1.0; // restitution (1 = elastic)

    double j = -(1+e)*relVel;
    j /= (1/a.mass + 1/b.mass);

    double impulseX = j*nx;
    double impulseY = j*ny;

    a.vx += impulseX/a.mass;
    a.vy += impulseY/a.mass;

    b.vx -= impulseX/b.mass;
    b.vy -= impulseY/b.mass;
}

int main()
{
    Particle p1{0,0,1,0,1,0.5};
    Particle p2{5,0,-1,0,1,0.5};

    double dt = 0.01;

    for(int step=0; step<500; step++)
    {
        p1.x += p1.vx*dt;
        p1.y += p1.vy*dt;

        p2.x += p2.vx*dt;
        p2.y += p2.vy*dt;

        if(distance(p1,p2) <= p1.radius + p2.radius)
        {
            resolveCollision(p1,p2);
        }

        std::cout << "Step " << step
                  << " | P1(" << p1.x << "," << p1.y << ")"
                  << " P2(" << p2.x << "," << p2.y << ")"
                  << std::endl;
    }

    return 0;
}
