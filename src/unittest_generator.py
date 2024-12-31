from typing import Dict

class UnittestGenerator:
    def generate_unittest_code(self, code: str, test_cases: Dict) -> str:
        """Generate unittest code from test cases"""
        unittest_code = """
import unittest
from typing import *
import pytest
from unittest.mock import Mock, patch
"""

        # Add original code
        unittest_code += f"\n{code}\n\n"

        # Generate test class
        unittest_code += """
class GeneratedTests(unittest.TestCase):
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass

    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass
"""

        # Add test methods
        for test in test_cases.get('test_cases', []):
            unittest_code += self._generate_test_method(test)

        return unittest_code

    def _generate_test_method(self, test: Dict) -> str:
        """Generate a single test method"""
        inputs = test['inputs']
        input_str = ', '.join([f"{k}={v}" for k, v in inputs.items()])

        if test['category'] == 'error_case':
            return f"""
    def {test['name']}(self):
        \"\"\"
        {test['description']}
        \"\"\"
        with self.assertRaises(Exception):
            {test['function']}({input_str})
"""
        else:
            return f"""
    def {test['name']}(self):
        \"\"\"
        {test['description']}
        \"\"\"
        result = {test['function']}({input_str})
        self.assertEqual(result, {test['expected_output']})
"""