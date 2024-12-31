import json
import re
from typing import Dict

class ResultAnalyzer:
    def __init__(self, model):
        self.model = model

    def analyze_test_results(self, test_output: str) -> Dict:
        """Analyze test results and provide feedback"""
        prompt = f"""
        Analyze these test results and provide feedback:
        ```
        {test_output}
        ```

        Provide analysis in JSON format:
        {{
            "summary": {{
                "total_tests": number,
                "passed": number,
                "failed": number,
                "errors": number
            }},
            "score": number (0-5),
            "feedback": "detailed feedback",
            "recommendations": [
                "specific recommendations"
            ],
            "code_quality_metrics": {{
                "test_coverage": "percentage",
                "complexity": "low|medium|high",
                "maintainability": "good|fair|poor"
            }}
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error analyzing results: {e}")
            return self._generate_fallback_analysis(test_output)

    def _generate_fallback_analysis(self, test_output: str) -> Dict:
        """Generate basic analysis when LLM fails"""
        total_tests = len(re.findall(r'\.{3} ok|\.{3} FAIL|\.{3} ERROR', test_output))
        passed = len(re.findall(r'\.{3} ok', test_output))
        failed = total_tests - passed

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": len(re.findall(r'\.{3} ERROR', test_output))
            },
            "score": round((passed / total_tests * 5) if total_tests > 0 else 0, 1),
            "feedback": f"Passed {passed} out of {total_tests} tests.",
            "recommendations": ["Review failed tests", "Add more test cases"],
            "code_quality_metrics": {
                "test_coverage": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "complexity": "medium",
                "maintainability": "fair"
            }
        }