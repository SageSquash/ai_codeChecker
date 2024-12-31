import json
import re
from typing import Dict, Optional

class TestCaseGenerator:
    def __init__(self, model):
        self.model = model

    def generate_test_cases(self, code: str) -> Dict:
        """Generate comprehensive test cases"""
        prompt = f"""
        Generate comprehensive test cases for this Python code.
        Return ONLY a JSON object in this exact format:
        {{
            "test_cases": [
                {{
                    "name": "test_name",
                    "category": "happy_path",
                    "function": "function_name",
                    "inputs": {{
                        "param1": "value1"
                    }},
                    "expected_output": "expected_result",
                    "description": "test description"
                }}
            ],
            "setup": {{
                "imports": ["required_import1"],
                "fixtures": ["fixture1"]
            }}
        }}

        Code to test:
        ```python
        {code}
        ```

        Include test cases for:
        1. Basic functionality (happy paths)
        2. Edge cases
        3. Error cases
        4. Input validation
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_test_cases_response(response.text)
        except Exception as e:
            print(f"Error generating test cases: {e}")
            return self._generate_basic_test_cases(code)

    def _parse_test_cases_response(self, response_text: str) -> Dict:
        """Parse the LLM response into test cases"""
        # Similar JSON parsing logic as in CodeAnalyzer
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]

        json_str = re.sub(r'(?<!\\)"(\w+)":', r'"\1":', json_str)
        json_str = json_str.replace("'", '"')
        return json.loads(json_str)

    def _generate_basic_test_cases(self, code: str) -> Dict:
        """Generate basic test cases when LLM fails"""
        return {
            "test_cases": [
                {
                    "name": "test_basic_functionality",
                    "category": "happy_path",
                    "function": "main_function",
                    "inputs": {},
                    "expected_output": "expected_result",
                    "description": "Basic functionality test"
                }
            ],
            "setup": {
                "imports": ["unittest"],
                "fixtures": []
            }
        }