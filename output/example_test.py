import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from example import *

import unittest
from example import Person, Color, fibonacci, main

class TestExample(unittest.TestCase):

    def test_person(self):
        """Test creating a Person namedtuple."""
        person = Person(name="Alice", age=30, city="Wonderland")
        self.assertEqual(person.name, "Alice")
        self.assertEqual(person.age, 30)
        self.assertEqual(person.city, "Wonderland")

    def test_combinations(self):
        """Test generating combinations using itertools."""
        items = ['A', 'B', 'C']
        combinations_list = list(combinations(items, 2))
        self.assertEqual(combinations_list, [('A', 'B'), ('A', 'C'), ('B', 'C')])

    def test_fibonacci(self):
        """Test computing Fibonacci numbers using lru_cache."""
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_statistics(self):
        """Test calculating mean and median using statistics."""
        data = [10, 20, 30, 40, 50]
        self.assertAlmostEqual(statistics.mean(data), 30.0)
        self.assertEqual(statistics.median(data), 30)

    def test_color_enum(self):
        """Test working with constants using Enum."""
        self.assertEqual(Color.RED.name, "RED")
        self.assertEqual(Color.GREEN.value, 2)
        self.assertIn(Color.BLUE, [Color.RED, Color.GREEN, Color.BLUE])

    def test_main(self):
        """Test the main function."""
        with self.assertRaises(TypeError):
            main(10)  # Passing an invalid argument

if __name__ == "__main__":
    unittest.main()