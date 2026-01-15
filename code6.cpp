#include <iostream>

// Folder 6 - C++ test file (code6.cpp)
long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    std::cout << "Folder 6 - code6.cpp test" << std::endl;
    std::cout << "factorial(6) = " << factorial(6) << std::endl;
    return 0;
}


