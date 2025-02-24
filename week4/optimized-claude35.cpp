
#include <iostream>
#include <iomanip>
#include <chrono>

double calculate(const int64_t iterations, const int64_t param1, const int64_t param2) {
    double result = 1.0;
    #pragma omp parallel for reduction(+:result) schedule(static)
    for (int64_t i = 1; i <= iterations; i++) {
        double j1 = i * static_cast<double>(param1) - param2;
        double j2 = i * static_cast<double>(param1) + param2;
        result += (1.0/j2 - 1.0/j1);
    }
    return result;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    
    double result = calculate(100000000, 4, 1) * 4;
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout << "Result: " << std::fixed << std::setprecision(12) << result << std::endl;
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) 
              << elapsed.count() << " seconds" << std::endl;
              
    return 0;
}
