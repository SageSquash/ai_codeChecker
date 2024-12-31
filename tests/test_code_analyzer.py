import unittest
from unittest.mock import Mock, patch
from src.code_analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.model = Mock()
        self.analyzer = CodeAnalyzer(self.model)

    def test_analyze_code(self):
        """Test code analysis"""
        test_code = "def test_function(): pass"
        mock_response = Mock()
        mock_response.text = '{"functions": [], "classes": []}'
        self.model.generate_content.return_value = mock_response

        result = self.analyzer.analyze_code(test_code)
        
        self.assertIsInstance(result, dict)
        self.assertIn('functions', result)
        self.assertIn('classes', result)
        self.model.generate_content.assert_called_once()

    def test_basic_analysis_fallback(self):
        """Test fallback analysis"""
        test_code = "class TestClass:\n    def test_method(self): pass"
        self.model.generate_content.side_effect = Exception("API Error")

        result = self.analyzer._generate_basic_analysis(test_code)
        
        self.assertIsInstance(result, dict)
        self.assertIn('classes', result)
        self.assertTrue(len(result['classes']) > 0)