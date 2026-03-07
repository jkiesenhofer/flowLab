/*#include <iostream>
#include <chrono> 
#include <thread>
#include <cstdlib>
#include <random>

int main() {
    int n = 5;
    std::random_device rd;   // Seed
    std::mt19937 gen(rd());  // Mersenne Twister engine

    // Define the range [1, 10]
    std::uniform_int_distribution<> dis(1, 10);
    
    for (int i = 0; i < n; i++) {

    // Generate a random number
    int randomNumber = dis(gen);
        
        std::cout << "########### CHART ###############" << randomNumber + 1 << std::endl;
        std::cout << "#  *       *****          **    #" << randomNumber + 1 << std::endl;
        std::cout << "#   *   ***     **       *  *   #" << randomNumber + 1 << std::endl;
        std::cout << "#    * *          **    *    *  #" << randomNumber + 1 << std::endl;
        std::cout << "#     *             ****        #" << randomNumber + 1 << std::endl;
        std::cout << "#################################" << randomNumber + 1 << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));
        #ifdef _WIN32
            system("CLS"); 
        #else
            system("clear");
        #endif
    }

    return 0;
}*/
#include <iostream>
#include <cmath>
#include <iomanip>

int main() {
    const int width = 100;   // horizontal size of the graph
    const int height = 25;   // vertical size of the graph
    const double pi = 3.14159265358979323846;
    std::cout << "#################################";
    std::cout << "#################################";
    std::cout << "#################################"<< std::endl;
    // Find max and min for scaling
    double maxVal = -1e9, minVal = 1e9;
    for (int x = 0; x < width; ++x) {
        double angle = (double)x / width * 10 * pi;  // choose scale to show enough cycles
        double y = 2 * sin(angle) - 5 * sin(0.8 * angle);
        if (y > maxVal) maxVal = y;
        if (y < minVal) minVal = y;
    }
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double angle = (double)x / width * 10 * pi;
            double value = 2 * sin(angle) - 5 * sin(0.8 * angle);

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
    std::cout << "#################################";
    std::cout << "#################################";
    std::cout << "#################################"<< std::endl;
    return 0;
}
