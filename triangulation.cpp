// triangulation.cpp
#include <iostream>
#include <cmath>
#include "collision.h"

using namespace std;

// Function to calculate triangle area using coordinates
double triangleArea(double x1, double y1,
                    double x2, double y2,
                    double x3, double y3)
{
    double area = abs(
        x1 * (y2 - y3) +
        x2 * (y3 - y1) +
        x3 * (y1 - y2)
    ) / 2.0;

    return area;
}

int main()
{
    double x1, y1, x2, y2, x3, y3;
    Particle p1{0,0,1,0,1,0.5};
    Particle p2{5,0,-1,0,1,0.5};

    double dt = 0.01;

    cout << "Enter coordinates of triangle:\n";

    cout << "Point 1 (x1 y1): ";
    cin >> x1 >> y1;

    cout << "Point 2 (x2 y2): ";
    cin >> x2 >> y2;

    cout << "Point 3 (x3 y3): ";
    cin >> x3 >> y3;

    double area = triangleArea(x1, y1, x2, y2, x3, y3);

    cout << "Area of the triangle: " << area << endl;

    for(int step=0; step<500; step++) {
        p1.x += p1.vx*dt;
        p1.y += p1.vy*dt;

        p2.x += p2.vx*dt;
        p2.y += p2.vy*dt;

        if(distance(p1,p2) <= p1.radius + p2.radius) {
            resolveCollision(p1,p2);
        }

        std::cout << "Step " << step
                  << " | P1(" << p1.x << "," << p1.y << ")"
                  << " P2(" << p2.x << "," << p2.y << ")"
                  << std::endl;
    }

    return 0;
}
