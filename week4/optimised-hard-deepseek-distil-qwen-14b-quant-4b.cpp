#include <vector>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <algorithm>

struct LCG {
    uint64_t a = 1664525;
    uint64_t c = 1013904223;
    uint64_t m = 2ULL << 32; // 2^32
    uint64_t value;

    LCG(uint64_t seed) : value(seed) {}

    uint64_t generate() {
        value = (a * value + c) % m;
        return value;
    }
};

int max_subarray_sum(int n, uint64_t seed, int min_val, int max_val) {
    LCG lcg(seed);
    std::vector<int64_t> random_numbers(n);
    for (int i = 0; i < n; ++i) {
        random_numbers[i] = lcg.generate() % (max_val - min_val + 1) + min_val;
    }

    int64_t max_sum = std::numeric_limits<int64_t>::min();
    int64_t current_sum = 0;

    for (int i = 0; i < n; ++i) {
        current_sum = std::max(random_numbers[i], current_sum + random_numbers[i]);
        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}

int total_max_subarray_sum(int n, uint64_t initial_seed, int min_val, int max_val) {
    LCG master_lcg(initial_seed);
    uint64_t seed = master_lcg.generate();
    int64_t total_sum = 0;

    for (int i = 0; i < 20; ++i) {
        uint64_t current_seed = seed;
        total_sum += max_subarray_sum(n, current_seed, min_val, max_val);
        seed = master_lcg.generate();
    }

    return total_sum;
}

int main() {
    const int n = 10000;
    const uint64_t initial_seed = 42;
    const int min_val = -10;
    const int max_val = 10;

    auto start = std::chrono::high_resolution_clock::now();
    int result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    auto end = std::chrono::high_resolution_clock::now();

    std::cout << "Total Maximum Subarray Sum (20 runs): " << result << std::endl;
    std::cout << "Execution Time: " << std::chrono::duration_cast<std::chrono::duration<double>>(end - start).count() << " seconds" << std::endl;

    return 0;
}