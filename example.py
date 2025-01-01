from collections import namedtuple
from itertools import combinations
from functools import lru_cache
import statistics
from enum import Enum, auto

# Using namedtuple to create a lightweight data structure
Person = namedtuple('Person', ['name', 'age', 'city'])

# Using enum to define a set of constants
class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

# Using lru_cache for memoization
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def main():
    # Using namedtuple
    person = Person(name="Alice", age=30, city="Wonderland")
    print(f"Person: {person.name}, {person.age}, {person.city}")

    # Using itertools to generate combinations
    items = ['A', 'B', 'C']
    print("Combinations of items:")
    for combo in combinations(items, 2):
        print(combo)

    # Using lru_cache to compute Fibonacci numbers
    print("Fibonacci sequence:")
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")

    # Using statistics to calculate mean and median
    data = [10, 20, 30, 40, 50]
    print(f"Mean: {statistics.mean(data)}")
    print(f"Median: {statistics.median(data)}")

    # Using enum to work with constants
    print("Colors:")
    for color in Color:
        print(color)

if __name__ == "__main__":
    main()