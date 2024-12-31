# src/test_generator.py

import google.generativeai as genai
from typing import Dict, List, Any
import json
import re
import os
import ast
from dataclasses import dataclass

@dataclass
class CodeAnalysis:
    """Structure to hold code analysis results"""
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    imports: List[str]
    module_name: str

class TestGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def read_python_file(self, file_path: str) -> str:
        """Read Python code from file"""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""

    def analyze_code(self, code: str, file_path: str) -> CodeAnalysis:
        """Analyze the Python code structure"""
        try:
            tree = ast.parse(code)
            analysis = {
                'functions': [],
                'classes': [],
                'imports': [],
                'module_name': os.path.splitext(os.path.basename(file_path))[0]
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Analyze function
                    func_info = {
                        'name': node.name,
                        'args': [{'name': arg.arg, 'type': self._get_type_hint(arg)} for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'docstring': ast.get_docstring(node),
                        'is_method': isinstance(node.parent, ast.ClassDef) if hasattr(node, 'parent') else False
                    }
                    analysis['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    # Analyze class
                    class_info = {
                        'name': node.name,
                        'methods': [],
                        'docstring': ast.get_docstring(node)
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': [{'name': arg.arg, 'type': self._get_type_hint(arg)} for arg in item.args.args],
                                'returns': self._get_return_type(item),
                                'docstring': ast.get_docstring(item)
                            }
                            class_info['methods'].append(method_info)
                    analysis['classes'].append(class_info)

            return CodeAnalysis(**analysis)

        except Exception as e:
            print(f"Error analyzing code: {e}")
            return CodeAnalysis(functions=[], classes=[], imports=[], module_name='module')

    def process_code(self, code: str, file_path: str) -> Dict:
        """Process the code and generate tests"""
        try:
            # Analyze the code
            analysis = self.analyze_code(code, file_path)
            
            # Generate prompt based on analysis
            prompt = self._generate_prompt(code, analysis)
            
            # Get AI response
            print("\nGenerating tests...")
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Process the response
            unittest_code = self._process_ai_response(response_text, analysis)
            test_cases = self._generate_test_cases(analysis)

            return {
                'test_cases': test_cases,
                'unittest_code': unittest_code
            }

        except Exception as e:
            print(f"Error in test generation: {e}")
            return self._generate_fallback_tests(code, file_path)

    def _generate_prompt(self, code: str, analysis: CodeAnalysis) -> str:
        """Generate appropriate prompt based on code analysis"""
        return f"""
        Generate comprehensive unit tests for this Python code:
        ```python
        {code}
        ```

        Code Structure:
        - Module: {analysis.module_name}
        - Functions: {[f['name'] for f in analysis.functions]}
        - Classes: {[c['name'] for c in analysis.classes]}

        Requirements:
        1. Generate complete unittest code with:
           - Proper imports (including the module being tested)
           - TestCase class(es) for functions and/or classes
           - setUp and tearDown methods if needed
           - Comprehensive test methods
           - Main block for running tests

        2. Include tests for:
           - Normal cases (expected inputs/outputs)
           - Edge cases (empty, boundary values)
           - Error cases (invalid inputs)
           - Type checking where appropriate

        3. Use appropriate assertions:
           - assertEqual for exact matches
           - assertAlmostEqual for floats
           - assertRaises for exceptions
           - assertTrue/assertFalse for booleans
           - assertIn for membership
           - assertIsInstance for type checking

        4. Include clear docstrings explaining each test's purpose

        Return only the unittest code in this format:
        ```python
        [Your unittest code here]
        ```
        """

    def _process_ai_response(self, response_text: str, analysis: CodeAnalysis) -> str:
        """Process and format the AI response into valid unittest code"""
        # Extract code from markdown if present
        code_match = re.search(r'```python(.*?)```', response_text, re.DOTALL)
        unittest_code = code_match.group(1) if code_match else response_text

        # Clean up the code
        unittest_code = unittest_code.strip()

        # Add imports
        imports = f"""import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from {analysis.module_name} import *
"""

        # Ensure proper test class structure
        if 'class Test' not in unittest_code:
            class_name = analysis.classes[0]['name'] if analysis.classes else 'Functions'
            unittest_code = f"""
class Test{class_name}(unittest.TestCase):
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass

    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass

{unittest_code}
"""

        # Add main block if not present
        if '__main__' not in unittest_code:
            unittest_code += "\n\nif __name__ == '__main__':\n    unittest.main()"

        return f"{imports}\n{unittest_code}"

    def _generate_test_cases(self, analysis: CodeAnalysis) -> Dict:
        """Generate structured test cases based on code analysis"""
        test_cases = {"test_cases": []}

        # Generate test cases for standalone functions
        for func in analysis.functions:
            if not func['is_method']:
                test_cases['test_cases'].extend(self._generate_function_test_cases(func))

        # Generate test cases for classes and their methods
        for class_info in analysis.classes:
            for method in class_info['methods']:
                test_cases['test_cases'].extend(self._generate_method_test_cases(class_info['name'], method))

        return test_cases

    def _generate_function_test_cases(self, func: Dict) -> List[Dict]:
        """Generate test cases for a function"""
        return [{
            "name": f"test_{func['name']}_basic",
            "function": func['name'],
            "inputs": {arg['name']: self._get_default_value(arg['type']) for arg in func['args']},
            "expected_output": None,
            "description": f"Basic test for {func['name']}"
        }]

    def _generate_method_test_cases(self, class_name: str, method: Dict) -> List[Dict]:
        """Generate test cases for a class method"""
        return [{
            "name": f"test_{method['name']}_basic",
            "class": class_name,
            "method": method['name'],
            "inputs": {arg['name']: self._get_default_value(arg['type']) for arg in method['args']},
            "expected_output": None,
            "description": f"Basic test for {class_name}.{method['name']}"
        }]

    def _get_type_hint(self, node: ast.arg) -> str:
        """Extract type hint from AST node"""
        return getattr(node, 'annotation', None).__class__.__name__ if hasattr(node, 'annotation') else 'Any'

    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type from function definition"""
        return node.returns.__class__.__name__ if hasattr(node, 'returns') and node.returns else 'Any'

    def _get_default_value(self, type_hint: str) -> Any:
        """Get default value based on type hint"""
        defaults = {
            'str': '',
            'int': 0,
            'float': 0.0,
            'bool': False,
            'list': [],
            'dict': {},
            'tuple': (),
            'set': set(),
        }
        return defaults.get(type_hint, None)

    def _generate_fallback_tests(self, code: str, file_path: str) -> Dict:
        """Generate basic tests when AI generation fails"""
        analysis = self.analyze_code(code, file_path)
        test_cases = self._generate_test_cases(analysis)
        unittest_code = self._process_ai_response("", analysis)
        return {
            'test_cases': test_cases,
            'unittest_code': unittest_code
        }