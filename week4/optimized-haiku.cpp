
#include <iostream>
#include <iomanip>
#include <chrono>

double calculate(int iterations, int param1, int param2) {
    double result = 1.0;
    for (int i = 1; i <= iterations; ++i) {
        long long j = (long long)i * param1 - param2;
        result -= 1.0 / j;
        j = (long long)i * param1 + param2;
        result += 1.0 / j;
    }
    return result;
}

int main() {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    double result = calculate(100'000'000, 4, 1) * 4;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end_time - start_time;
    
    std::cout << std::fixed << std::setprecision(12) 
              << "Result: " << result << std::endl;
    std::cout << "Execution Time: " << duration.count() << " seconds" << std::endl;
    
    return 0;
}
