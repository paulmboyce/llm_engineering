
#include <iostream>
#include <vector>
#include <chrono>
#include <limits>
#include <iomanip>

class LCG {
private:
    uint64_t value;
    static constexpr uint64_t a = 1664525;
    static constexpr uint64_t c = 1013904223;
    static constexpr uint64_t m = 1ULL << 32;
    
public:
    LCG(uint64_t seed) : value(seed) {}
    
    uint64_t next() {
        value = (a * value + c) % m;
        return value;
    }
};

int64_t max_subarray_sum(int n, uint64_t seed, int min_val, int max_val) {
    LCG lcg(seed);
    std::vector<int64_t> nums(n);
    
    uint64_t range = max_val - min_val + 1;
    for(int i = 0; i < n; i++) {
        nums[i] = (lcg.next() % range) + min_val;
    }

    int64_t max_sum = std::numeric_limits<int64_t>::min();
    int64_t curr_sum;
    
    for(int i = 0; i < n; i++) {
        curr_sum = 0;
        for(int j = i; j < n; j++) {
            curr_sum += nums[j];
            max_sum = std::max(max_sum, curr_sum);
        }
    }
    
    return max_sum;
}

int64_t total_max_subarray_sum(int n, uint64_t initial_seed, int min_val, int max_val) {
    int64_t total = 0;
    LCG lcg(initial_seed);
    
    for(int i = 0; i < 20; i++) {
        total += max_subarray_sum(n, lcg.next(), min_val, max_val);
    }
    return total;
}

int main() {
    const int n = 10000;
    const uint64_t initial_seed = 42;
    const int min_val = -10;
    const int max_val = 10;

    auto start = std::chrono::high_resolution_clock::now();
    int64_t result = total_max_subarray_sum(n, initial_seed, min_val, max_val);
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double> diff = end - start;
    
    std::cout << "Total Maximum Subarray Sum (20 runs): " << result << std::endl;
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) 
              << diff.count() << " seconds" << std::endl;
              
    return 0;
}
