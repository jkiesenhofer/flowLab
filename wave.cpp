#include <iostream>
#include <cmath>
#include <iomanip>
#include <list>

class dyn {
    private:
        static int value2;
    };
int dyn::value2 = 0;

int main() {
    const int width = 100;   // horizontal size of the graph
    const int height = 25;   // vertical size of the graph
    const double pi = 3.14159265358979323846;
    //std::cout << "#################################";
    //std::cout << "#################################";
    //std::cout << "#################################"<< std::endl;
    // Find max and min for scaling
    double maxVal = -1e9, minVal = 1e9;
    std::list<int> myList = {1, 2, 3, 4, 5};
    int* ptr = nullptr;
    double width2[3] = {10.5, 20.75, 30.0};
    for (int x = 0; x < width; ++x) {
        double angle = (double)x / width * 10 * pi;  // choose scale to show enough cycles
        double y = 2 * sin(angle) - 5 * sin(0.8 * angle);
        if (y > maxVal) maxVal = y;
        if (y < minVal) minVal = y;
    }
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double angle = (double)x / width * 10 * pi;
            double value = 0.4 * sin(angle) - 2 * sin(0.8 * angle);

            // Map value to row
            int row = (int)((value - minVal) / (maxVal - minVal) * (height - 1));

            if (height - y - 1 == row) {
                std::cout << "*";
            } else {
                std::cout << " ";
            }
        }
        std::cout << std::endl;
        
    }
    //std::cout << "#################################";
    //std::cout << "#################################";
    //std::cout << "#################################"<< std::endl;
    return 0;
}
