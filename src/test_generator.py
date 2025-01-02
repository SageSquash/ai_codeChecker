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
                    func_info = {
                        'name': node.name,
                        'args': [{'name': arg.arg, 'type': self._get_type_hint(arg)} for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'docstring': ast.get_docstring(node),
                        'is_method': isinstance(node.parent, ast.ClassDef) if hasattr(node, 'parent') else False
                    }
                    analysis['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
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
            analysis = self.analyze_code(code, file_path)
            prompt = self._generate_prompt(code, analysis)
            
            print("\nGenerating tests...")
            response = self.model.generate_content(prompt)
            response_text = response.text

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
        code_match = re.search(r'```python(.*?)```', response_text, re.DOTALL)
        unittest_code = code_match.group(1) if code_match else response_text

        unittest_code = unittest_code.strip()

        imports = f"""import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from {analysis.module_name} import *
"""

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

        if '__main__' not in unittest_code:
            unittest_code += "\n\nif __name__ == '__main__':\n    unittest.main()"

        return f"{imports}\n{unittest_code}"

    def _generate_test_cases(self, analysis: CodeAnalysis) -> Dict:
        """Generate structured test cases based on code analysis"""
        test_cases = {"test_cases": []}

        for func in analysis.functions:
            if not func['is_method']:
                test_cases['test_cases'].extend(self._generate_function_test_cases(func))

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


    def generate_feedback(self, test_output: str, code: str) -> Dict:
        """Generate feedback based on test results"""
        try:
            print("\n=== Parsing Test Results ===")
        
            # Improved test result parsing
            # Look for the summary line that shows total tests run
            summary_match = re.search(r'Ran (\d+) tests? in', test_output)
            total_tests = int(summary_match.group(1)) if summary_match else 0
        
            # Count passed tests (tests that show "ok")
            passed = len(re.findall(r' \.\.\. ok', test_output))
        
            # Count failed tests (tests that show "FAIL")
            failed = len(re.findall(r' \.\.\. FAIL', test_output))
        
            # Count error tests (tests that show "ERROR")
            errors = len(re.findall(r' \.\.\. ERROR', test_output))
        
            print(f"Found: {total_tests} total, {passed} passed, {failed} failed, {errors} errors")
        
            # Calculate metrics
            pass_percentage = (passed / total_tests * 100) if total_tests > 0 else 0
            score = (passed / total_tests * 5) if total_tests > 0 else 0
        
            print(f"Pass rate: {pass_percentage:.1f}%")
            print(f"Initial score: {score:.1f}/5.0")
        
            try:
                print("\n=== Attempting AI Feedback Generation ===")
                # Try AI feedback
                prompt = f"""
                Analyze these test results and provide feedback. Return only a JSON object without any additional text or formatting.

                Test Summary:
                - Total tests: {total_tests}
                - Passed: {passed}
                - Failed: {failed}
                - Errors: {errors}
                - Pass rate: {pass_percentage:.1f}%
                
                Test Output:
                {test_output}
                
                Return exactly this JSON structure:
                {{
                    "score": {score},
                    "summary": {{
                        "total_tests": {total_tests},
                        "passed": {passed},
                        "failed": {failed},
                        "errors": {errors}
                    }},
                    "code_quality": {{
                        "complexity": "low",
                        "maintainability": "good",
                        "test_coverage": "{pass_percentage:.1f}%"
                    }},
                    "detailed_feedback": {{
                        "strengths": [
                            "All tests passing successfully",
                            "Good test organization"
                        ],
                        "weaknesses": [],
                        "recommendations": [
                            "Consider adding more edge cases",
                            "Add performance tests"
                        ]
                    }},
                    "security_considerations": [],
                    "performance_insights": {{
                        "efficiency": "Good",
                        "bottlenecks": [],
                        "optimization_suggestions": []
                    }}
                }}
                """
                
                print("Sending request to AI model...")
                response = self.model.generate_content(prompt)
                print("Received response from AI model")
                
                try:
                    print("Parsing AI response...")
                    # Clean the response text
                    response_text = response.text.strip()
                    
                    # Remove "JSON" prefix if present
                    if response_text.startswith("JSON"):
                        response_text = response_text[4:].strip()
                    
                    # Remove any markdown formatting if present
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].strip()
                    
                    print("\nCleaned response text:")
                    print(response_text)
                    
                    # Try to find JSON object in the response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        response_text = json_match.group(0)
                    
                    feedback = json.loads(response_text)
                    print("Successfully parsed AI feedback")
                    
                    # Ensure the metrics are correct
                    feedback['score'] = score
                    feedback['summary'] = {
                        "total_tests": total_tests,
                        "passed": passed,
                        "failed": failed,
                        "errors": errors
                    }
                    feedback['code_quality']['test_coverage'] = f"{pass_percentage:.1f}%"
                    feedback['ai_generated'] = True
                    
                    print("=== Using AI-Generated Feedback ===")
                    return feedback
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse AI response: {e}")
                    print("Response text:", response_text)
                    print("Falling back to calculated feedback")
                    return self._generate_calculated_feedback(total_tests, passed, failed, errors)
                    
            except Exception as e:
                print(f"AI feedback generation failed: {e}")
                print("Falling back to calculated feedback")
                return self._generate_calculated_feedback(total_tests, passed, failed, errors)
                
        except Exception as e:
            print(f"Error in feedback generation: {e}")
            print("Falling back to basic calculated feedback")
            return self._generate_calculated_feedback(0, 0, 0, 0)

    def _generate_calculated_feedback(self, total_tests: int, passed: int, failed: int, errors: int) -> Dict:
        """Generate feedback based on test statistics"""
        print("\n=== Generating Calculated Feedback ===")
        pass_percentage = (passed / total_tests * 100) if total_tests > 0 else 0
        score = (passed / total_tests * 5) if total_tests > 0 else 0
        
        print(f"Calculating feedback for: {passed}/{total_tests} tests passed ({pass_percentage:.1f}%)")
        
        # Determine quality ratings based on pass percentage
        if pass_percentage == 100:
            complexity = "low"
            maintainability = "good"
            efficiency = "good"
        elif pass_percentage >= 80:
            complexity = "low"
            maintainability = "good"
            efficiency = "good"
        elif pass_percentage >= 60:
            complexity = "medium"
            maintainability = "fair"
            efficiency = "fair"
        else:
            complexity = "high"
            maintainability = "poor"
            efficiency = "poor"

        # Generate appropriate feedback messages
        strengths = []
        weaknesses = []
        recommendations = []

        # Add specific feedback based on test results
        if passed == total_tests:
            strengths.append("All tests passing successfully")
            strengths.append("Perfect pass rate achieved")
        elif passed > 0:
            strengths.append(f"Successfully passed {passed} out of {total_tests} tests")
        
        if failed > 0:
            weaknesses.append(f"Found {failed} failing test(s)")
            recommendations.append("Fix failing tests to improve reliability")
        
        if errors > 0:
            weaknesses.append(f"Encountered {errors} test error(s)")
            recommendations.append("Address test errors to ensure proper execution")
        
        if total_tests < 10:
            recommendations.append("Consider adding more test cases for better coverage")
        
        # Add default messages if needed
        if not strengths:
            strengths.append("Basic test structure implemented")
        if not weaknesses and pass_percentage == 100:
            strengths.append("No failing tests or errors")
        if not recommendations:
            recommendations.append("Consider adding more comprehensive tests")

        return {
            "score": round(score, 1),
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors
            },
            "code_quality": {
                "complexity": complexity,
                "maintainability": maintainability,
                "test_coverage": f"{pass_percentage:.1f}%",
                "best_practices": [
                    f"Test suite with {total_tests} tests implemented",
                    f"{passed}/{total_tests} tests passing successfully"
                ],
                "areas_of_concern": [
                    f"{failed} failing tests" if failed > 0 else "No failing tests",
                    f"{errors} test errors" if errors > 0 else "No test errors"
                ]
            },
            "detailed_feedback": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations
            },
            "test_quality": {
                "coverage_assessment": f"Test coverage: {pass_percentage:.1f}%",
                "edge_cases": "Consider adding more edge cases" if total_tests < 10 else "Good test coverage",
                "assertion_quality": f"{passed}/{total_tests} tests passing successfully"
            },
            "security_considerations": [
                "Basic security tests in place" if total_tests > 5 else "Consider adding security-specific tests",
                "Review input validation coverage"
            ],
            "performance_insights": {
                "efficiency": efficiency,
                "bottlenecks": [
                    "No major bottlenecks detected" if failed == 0 and errors == 0 else "Address failing tests",
                    f"{failed} failing tests need attention" if failed > 0 else "All tests passing"
                ],
                "optimization_suggestions": [
                    "Consider adding performance tests",
                    "Add more edge cases" if total_tests < 10 else "Good test coverage"
                ]
            }
        }