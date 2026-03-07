// triangulation.cpp
#include <iostream>
#include <cmath>

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

    cout << "Enter coordinates of triangle:\n";

    cout << "Point 1 (x1 y1): ";
    cin >> x1 >> y1;

    cout << "Point 2 (x2 y2): ";
    cin >> x2 >> y2;

    cout << "Point 3 (x3 y3): ";
    cin >> x3 >> y3;

    double area = triangleArea(x1, y1, x2, y2, x3, y3);

    cout << "Area of the triangle: " << area << endl;

    return 0;
}
