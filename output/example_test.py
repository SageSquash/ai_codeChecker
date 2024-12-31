import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from example import *

import unittest
import example

class TestCalculateCircleArea(unittest.TestCase):

    def test_calculate_circle_area_positive_radius(self):
        """
        Test calculate_circle_area() with a positive radius.
        """
        radius = 5
        expected_area = 78.54
        actual_area = example.calculate_circle_area(radius)
        self.assertAlmostEqual(actual_area, expected_area, delta=0.01)

    def test_calculate_circle_area_negative_radius(self):
        """
        Test calculate_circle_area() with a negative radius.
        """
        radius = -3
        expected_error_message = "Radius cannot be negative."
        with self.assertRaises(Exception) as e:
            example.calculate_circle_area(radius)
        self.assertEqual(str(e.exception), expected_error_message)

    def test_calculate_circle_area_zero_radius(self):
        """
        Test calculate_circle_area() with a zero radius.
        """
        radius = 0
        expected_area = 0
        actual_area = example.calculate_circle_area(radius)
        self.assertEqual(actual_area, expected_area)

    def test_calculate_circle_area_invalid_input(self):
        """
        Test calculate_circle_area() with an invalid input (not a number).
        """
        with self.assertRaises(ValueError):
            example.calculate_circle_area("abc")


if __name__ == '__main__':
    unittest.main()