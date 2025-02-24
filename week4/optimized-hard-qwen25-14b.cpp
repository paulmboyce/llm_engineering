
#include <iostream>
#include <vector>
#include <limits>
#include <ctime>

// Linear Congruential Generator
unsigned int lcg(unsigned int& seed, unsigned int a = 1664525, unsigned int c = 1013904223, unsigned int m = 1U << 32) {
    return (a * seed + c) % m;
}

int max_subarray_sum(int n, unsigned int seed, int min_val, int max_val) {
    std::vector<int> random_numbers(n);
    unsigned int lcg_seed = seed;
    for (int i = 0; i < n; ++i) {
        random_numbers[i] = lcg(lcg_seed) % (max_val - min_val + 1) + min_val;
    }

    int max_sum = std::numeric_limits<int>::min();
    for (int i = 0; i < n; ++i) {
        int current_sum = 0;
        for (int j = i; j < n; ++j) {
            current_sum += random_numbers[j];
            if (current_sum > max_sum) {
                max_sum = current_sum;
            }
        }
    }
    return max_sum;
}

int total_max_subarray_sum(int n, unsigned int initial_seed, int min_val, int max_val) {
    int total_sum = 0;
    unsigned int lcg_seed = initial_seed;
    for (int i = 0; i < 20; ++i) {
        unsigned int seed = lcg(lcg_seed);
        total_sum += max_subarray_sum(n, seed, min_val, max_val);
    }
    return total_sum;
}

int main() {
    int n = 10000;         // Number of random numbers
    unsigned int initial_seed = 42; // Initial seed for the LCG
    int min_val = -10;     // Minimum value of random numbers
    int max_val = 10;      // Maximum value of random numbers

    // Timing the function
    clock_t start_time = clock();
    int result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    clock_t end_time = clock();

    std::cout << "Total Maximum Subarray Sum (20 runs): " << result << std::endl;
    std::cout << "Execution Time: " << static_cast<double>(end_time - start_time) / CLOCKS_PER_SEC << " seconds" << std::endl;

    return 0;
}
