import json
import re
from typing import Dict, Optional

class CodeAnalyzer:
    def __init__(self, model):
        self.model = model

    def analyze_code(self, code: str) -> Dict:
        """Analyze code to determine its structure and requirements"""
        prompt = f"""
        Analyze this Python code and provide information about its structure.
        Return ONLY a JSON object in this exact format:
        {{
            "functions": [
                {{
                    "name": "function_name",
                    "parameters": [
                        {{
                            "name": "parameter_name",
                            "type": "parameter_type"
                        }}
                    ],
                    "return_type": "return_type",
                    "description": "function description"
                }}
            ],
            "classes": [
                {{
                    "name": "class_name",
                    "methods": [
                        {{
                            "name": "method_name",
                            "parameters": [
                                {{
                                    "name": "parameter_name",
                                    "type": "parameter_type"
                                }}
                            ],
                            "return_type": "return_type",
                            "description": "method description"
                        }}
                    ]
                }}
            ],
            "dependencies": [
                "required_package_1",
                "required_package_2"
            ]
        }}

        Code to analyze:
        ```python
        {code}
        ```
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_analysis_response(response.text)
        except Exception as e:
            print(f"Error in code analysis: {e}")
            return self._generate_basic_analysis(code)

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the LLM response into a structured format"""
        # Extract JSON content
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]

        # Clean up and parse JSON
        json_str = re.sub(r'(?<!\\)"(\w+)":', r'"\1":', json_str)
        json_str = json_str.replace("'", '"')
        return json.loads(json_str)

    def _generate_basic_analysis(self, code: str) -> Dict:
        """Generate basic code analysis when LLM fails"""
        analysis = {
            "functions": [],
            "classes": [],
            "dependencies": []
        }

        # Find classes
        class_matches = re.finditer(r'class\s+(\w+):', code)
        for match in class_matches:
            class_name = match.group(1)
            analysis["classes"].append({
                "name": class_name,
                "methods": []
            })

        # Find imports
        import_matches = re.finditer(r'import\s+(\w+)|from\s+(\w+)', code)
        for match in import_matches:
            dep = match.group(1) or match.group(2)
            if dep not in analysis["dependencies"]:
                analysis["dependencies"].append(dep)

        return analysis