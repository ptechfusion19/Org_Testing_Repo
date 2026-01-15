#!/usr/bin/env python3
"""
Folder 6 - Python test script (script6.py)
"""


def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    print("Folder 6 - script6.py")
    print("fib(6) =", fibonacci(6))


