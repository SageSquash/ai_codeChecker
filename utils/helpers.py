import os
import re
from typing import Dict, List, Optional, Any
import ast
import json

class file_operations:
    """File operation utilities"""
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read content from a file"""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            raise FileNotFoundError(f"Error reading file {file_path}: {str(e)}")

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """Write content to a file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
        except Exception as e:
            raise IOError(f"Error writing to file {file_path}: {str(e)}")

class code_parser:
    """Code parsing utilities"""
    @staticmethod
    def extract_functions(code: str) -> List[Dict]:
        """Extract function definitions from code"""
        try:
            tree = ast.parse(code)
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': node.returns.id if node.returns else None
                    })
            return functions
        except Exception as e:
            print(f"Error parsing code: {e}")
            return []

    @staticmethod
    def extract_classes(code: str) -> List[Dict]:
        """Extract class definitions from code"""
        try:
            tree = ast.parse(code)
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'methods': [method.name for method in node.body 
                                  if isinstance(method, ast.FunctionDef)]
                    })
            return classes
        except Exception as e:
            print(f"Error parsing code: {e}")
            return []

class string_utils:
    """String manipulation utilities"""
    @staticmethod
    def clean_json_string(json_str: str) -> str:
        """Clean and format JSON string"""
        json_str = re.sub(r'(?<!\\)"(\w+)":', r'"\1":', json_str)
        json_str = json_str.replace("'", '"')
        return json_str

    @staticmethod
    def extract_json_from_text(text: str) -> str:
        """Extract JSON content from text"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].strip()
        else:
            start = text.find('{')
            end = text.rfind('}') + 1
            return text[start:end] if start != -1 and end != 0 else ""

class test_helpers:
    """Test-related utilities"""
    @staticmethod
    def format_test_name(function_name: str, scenario: str) -> str:
        """Format test method name"""
        return f"test_{function_name}_{scenario.lower().replace(' ', '_')}"

    @staticmethod
    def generate_test_docstring(description: str) -> str:
        """Generate formatted test docstring"""
        return f'"""\n        {description}\n        """'

    @staticmethod
    def parse_test_results(output: str) -> Dict[str, Any]:
        """Parse test execution results"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0
        }
        
        results['total'] = len(re.findall(r'test_\w+', output))
        results['passed'] = len(re.findall(r'ok', output))
        results['failed'] = len(re.findall(r'FAIL', output))
        results['errors'] = len(re.findall(r'ERROR', output))
        
        return results