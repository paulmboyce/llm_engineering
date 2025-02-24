
#include <iostream>
#include <cstdint>
#include <ctime>
#include <chrono>
#include <algorithm>

class Lcg {
private:
    uint32_t value;
    const uint32_t a;
    const uint32_t c;
    const uint32_t m;
public:
    Lcg(uint32_t seed, uint32_t a = 1664525, uint32_t c = 1013904223, uint32_t m = 0xFFFFFFFF)
        : value(seed), a(a), c(c), m(m) {}
    
    uint32_t next() {
        value = (a * value + c) % m;
        return value;
    }
};

int max_subarray_sum(int n, uint32_t seed, int min_val, int max_val) {
    Lcg lcg(seed);
    int random_numbers[n];
    for (int i = 0; i < n; ++i) {
        random_numbers[i] = (lcg.next() % (max_val - min_val + 1)) + min_val;
    }
    
    int max_sum = INT_MIN;
    int current_sum = 0;
    for (int i = 0; i < n; ++i) {
        current_sum = std::max(random_numbers[i], current_sum + random_numbers[i]);
        max_sum = std::max(max_sum, current_sum);
    }
    return max_sum;
}

int total_max_subarray_sum(int n, uint32_t initial_seed, int min_val, int max_val) {
    Lcg lcg(initial_seed);
    int total_sum = 0;
    for (int i = 0; i < 20; ++i) {
        uint32_t seed = lcg.next();
        total_sum += max_subarray_sum(n, seed, min_val, max_val);
    }
    return total_sum;
}

int main() {
    const int n = 10000;
    const uint32_t initial_seed = 42;
    const int min_val = -10;
    const int max_val = 10;

    auto start_time = std::chrono::high_resolution_clock::now();
    int result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    auto end_time = std::chrono::high_resolution_clock::now();

    std::cout << "Total Maximum Subarray Sum (20 runs): " << result << std::endl;
    std::cout << "Execution Time: " 
              << std::chrono::duration_cast<std::chrono::duration<double>>(end_time - start_time).count()
              << " seconds" << std::endl;

    return 0;
}