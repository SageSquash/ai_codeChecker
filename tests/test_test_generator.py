import unittest
from unittest.mock import Mock, patch
from src.test_generator import TestGenerator

class TestTestGenerator(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.test_generator = TestGenerator(self.api_key)

    def test_initialization(self):
        """Test TestGenerator initialization"""
        self.assertIsNotNone(self.test_generator.model)
        self.assertIsNotNone(self.test_generator.code_analyzer)
        self.assertIsNotNone(self.test_generator.test_case_generator)

    def test_read_python_file_success(self):
        """Test successful file reading"""
        with patch('builtins.open', unittest.mock.mock_open(read_data='test code')):
            result = self.test_generator.read_python_file('test.py')
            self.assertEqual(result, 'test code')

    def test_read_python_file_not_found(self):
        """Test file not found scenario"""
        result = self.test_generator.read_python_file('nonexistent.py')
        self.assertEqual(result, '')

    def test_process_code(self):
        """Test code processing"""
        test_code = "def test_function(): pass"
        with patch.object(self.test_generator.code_analyzer, 'analyze_code') as mock_analyze:
            with patch.object(self.test_generator.test_case_generator, 'generate_test_cases') as mock_generate:
                mock_analyze.return_value = {'analysis': 'test'}
                mock_generate.return_value = {'test_cases': []}
                
                result = self.test_generator.process_code(test_code)
                
                self.assertIn('analysis', result)
                self.assertIn('test_cases', result)
                mock_analyze.assert_called_once_with(test_code)
                mock_generate.assert_called_once_with(test_code)