import streamlit as st
import os
import json
import unittest
import importlib.util
from dotenv import load_dotenv
from src.test_generator import TestGenerator
from config.config import Config
from io import StringIO
import sys
import tempfile
import re
import time
import docker
import uuid
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PackageDetector:
    def __init__(self):
        self.required_packages = set()
        self.installed_packages = self._get_installed_packages()

    def _get_installed_packages(self):
        import pkg_resources
        return {pkg.key for pkg in pkg_resources.working_set}

    def scan_for_imports(self, code_content):
        import ast
        try:
            tree = ast.parse(code_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        package = alias.name.split('.')[0]
                        self.required_packages.add(package)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        self.required_packages.add(package)
        except Exception as e:
            logger.error(f"Error scanning imports: {e}")
        
        self.required_packages = {
            pkg for pkg in self.required_packages 
            if not self._is_stdlib_package(pkg)
        }
        return self.required_packages

    def _is_stdlib_package(self, package_name):
        import sys
        return package_name in sys.stdlib_module_names

    def get_missing_packages(self):
        return self.required_packages - self.installed_packages

class DockerTestRunner:
    def __init__(self):
        self.client = docker.from_env()
        self.image_name = 'python-test-runner'
        self.image_tag = 'v1'

    def run_test(self, code_content, test_content):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test files
                code_path = os.path.join(temp_dir, 'uploaded_code.py')
                test_path = os.path.join(temp_dir, 'test_uploaded_code.py')
                init_path = os.path.join(temp_dir, '__init__.py')
                
                # Write files
                with open(code_path, 'w') as f:
                    f.write(code_content)
                with open(test_path, 'w') as f:
                    f.write(test_content)
                with open(init_path, 'w') as f:
                    f.write('')
                
                # Run container
                container = self.client.containers.run(
                    f"{self.image_name}:{self.image_tag}",
                    command=['python', '-m', 'unittest', '-v', 'test_uploaded_code.py'],
                    volumes={
                        temp_dir: {'bind': '/app', 'mode': 'rw'}
                    },
                    working_dir='/app',
                    remove=True,
                    detach=False,
                    stdout=True,
                    stderr=True
                )
                
                return container.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Docker test execution error: {e}")
            return f"Error: {str(e)}"

def init_session_state():
    default_states = {
        'test_results': None,
        'feedback': None,
        'code_content': None,
        'generated_tests': None,
        'temp_dir': None,
        'current_file': None,
        'current_code': None,
        'docker_runner': None,
        'debug_info': []
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    if st.session_state.docker_runner is None:
        st.session_state.docker_runner = DockerTestRunner()

def reset_state():
    cleanup()
    for key in list(sys.modules.keys()):
        if 'uploaded_code' in key or 'test_uploaded_code' in key:
            del sys.modules[key]
    
    for key in list(st.session_state.keys()):
        if key != 'docker_runner':
            del st.session_state[key]
    
    init_session_state()

def generate_basic_feedback(test_output: str) -> dict:
    total_tests = len(re.findall(r'test_\w+', test_output))
    passed = len(re.findall(r' \.\.\. ok', test_output))
    failed = len(re.findall(r' \.\.\. FAIL', test_output))
    errors = len(re.findall(r' \.\.\. ERROR', test_output))
    
    pass_rate = passed / total_tests if total_tests > 0 else 0
    
    return {
        "language": "Python",
        "score": round(5.0 * pass_rate, 1),
        "scoring_explanation": f"Score based on {passed} passing tests out of {total_tests} total tests.",
        "summary": {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": pass_rate
        }
    }

def save_uploaded_code(code_content):
    try:
        if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
            cleanup()
        
        temp_dir = tempfile.mkdtemp()
        st.session_state.temp_dir = temp_dir
        
        code_path = os.path.join(temp_dir, "uploaded_code.py")
        with open(code_path, "w") as f:
            f.write(code_content)
        
        return temp_dir, code_path
    except Exception as e:
        logger.error(f"Error saving code: {e}")
        return None, None

def run_unittest_file(unittest_path: str, generator: TestGenerator, original_code: str, code_dir: str) -> dict:
    try:
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        def update_status(message: str, progress: int):
            status_container.text(message)
            progress_bar.progress(progress)
            logger.info(message)

        update_status("Running tests...", 40)
        test_output = st.session_state.docker_runner.run_test(
            original_code,
            open(unittest_path).read()
        )
        
        update_status("Processing results...", 70)
        
        # Parse test results
        summary_match = re.search(r'Ran (\d+) tests in', test_output)
        total_tests = int(summary_match.group(1)) if summary_match else 0
        passed_tests = test_output.count('... ok')
        failed_tests = len(re.findall(r' \.\.\. FAIL', test_output))
        error_tests = len(re.findall(r' \.\.\. ERROR', test_output))
        
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        update_status("Generating feedback...", 85)
        try:
            feedback = generator.generate_feedback(test_output, original_code)
            # Ensure feedback has all required components
            if 'summary' not in feedback:
                feedback['summary'] = {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'errors': error_tests,
                    'pass_rate': pass_rate
                }
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            feedback = generate_basic_feedback(test_output)

        results = {
            'output': test_output,
            'feedback': feedback,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'pass_rate': pass_rate
            },
            'success': pass_rate == 1.0
        }
        
        update_status("Complete", 100)
        return results

    except Exception as e:
        logger.error(f"Error in test execution: {e}")
        st.error(f"Error running tests: {e}")
        return None
    finally:
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_container' in locals():
            status_container.empty()


def display_feedback(feedback):
    """Display formatted feedback with all components"""
    try:
        st.markdown("""
            <h1 style='text-align: center; color: #1E88E5; padding-bottom: 20px;'>
                Evaluation Results
            </h1>
        """, unsafe_allow_html=True)
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tests", feedback.get('summary', {}).get('total_tests', 0))
        with col2:
            st.metric("Passed", feedback.get('summary', {}).get('passed', 0))
        with col3:
            st.metric("Failed", feedback.get('summary', {}).get('failed', 0))
        with col4:
            st.metric("Errors", feedback.get('summary', {}).get('errors', 0))

        # Display pass rate
        pass_rate = feedback.get('summary', {}).get('pass_rate', 0)
        st.progress(pass_rate)
        st.write(f"Pass Rate: {pass_rate*100:.1f}%")

        # Display overall score
        score = feedback.get('score', 0)
        st.write(f"Overall Score: {score:.2f}/5.0")

        # Display scoring explanation
        st.markdown("### 📝 Scoring Explanation")
        st.info(feedback.get('scoring_explanation', 'No explanation available.'))

        # Display identified issues without expanders
        if feedback.get('issues'):
            st.markdown("### 🔍 Identified Issues")
            for issue in feedback['issues']:
                st.markdown("---")  # Add separator between issues
                # Create container for each issue
                with st.container():
                    # Add severity indicator
                    severity_color = {
                        'High': '#F44336',
                        'Medium': '#FF9800',
                        'Low': '#4CAF50'
                    }.get(issue.get('severity', 'Unknown'), '#757575')
                    
                    st.markdown(f"""
                        <div style='
                            display: inline-block;
                            padding: 4px 12px;
                            border-radius: 15px;
                            background-color: {severity_color};
                            color: white;
                            font-size: 12px;
                            margin-bottom: 10px;'>
                            {issue.get('severity', 'Unknown')} Severity
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display issue description and fix
                    st.markdown(f"**Description:** {issue.get('description', 'No description available.')}")
                    st.markdown(f"**Fix:** {issue.get('fix', 'No fix suggestion available.')}")

    except Exception as e:
        logger.error(f"Error displaying feedback: {e}")
        st.error("Error displaying feedback. Please check the logs.")

def cleanup():
    try:
        if st.session_state.temp_dir and st.session_state.temp_dir in sys.path:
            sys.path.remove(st.session_state.temp_dir)
        
        if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        
        for key in list(sys.modules.keys()):
            if 'uploaded_code' in key or 'test_uploaded_code' in key:
                del sys.modules[key]
                
        if st.session_state.docker_runner:
            client = st.session_state.docker_runner.client
            for container in client.containers.list(all=True):
                if container.name.startswith('test_'):
                    try:
                        container.remove(force=True)
                    except:
                        pass
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def main():
    st.set_page_config(
        page_title="AI Test Generator",
        page_icon="🧪",
        layout="wide"
    )

    init_session_state()

    st.title("🧪 AI Test Generator")
    st.markdown("Generate unit tests for your Python code using AI")

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Google API Key", type="password")

        if st.button("Reset All"):
            if st.button("Confirm Reset"):
                reset_state()
                st.rerun()
    
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool uses AI to:
        - Generate unit tests
        - Analyze code quality
        - Provide detailed feedback
        - Suggest improvements
        """)

    tab1, tab2, tab3 = st.tabs(["Code Input", "Generated Tests", "Results"])
    
    with tab1:
        st.header("Code Input")
        input_method = st.radio(
            "Choose input method:",
            ["Upload Python File", "Paste Code"],
            horizontal=True
        )

        if input_method == "Upload Python File":
            uploaded_file = st.file_uploader("Upload Python file", type=["py"])
            if uploaded_file:
                if st.session_state.current_file != uploaded_file.name:
                    reset_state()
                    st.session_state.current_file = uploaded_file.name
                st.session_state.code_content = uploaded_file.getvalue().decode("utf-8")
                st.code(st.session_state.code_content, language="python")
        else:
            current_code = st.text_area(
                "Paste your Python code here",
                height=300,
                help="Enter your Python code here"
            )
            if current_code != st.session_state.current_code:
                reset_state()
                st.session_state.current_code = current_code
                st.session_state.code_content = current_code

        if st.button("Generate Tests", disabled=not (api_key and st.session_state.code_content)):
            cleanup()
            st.session_state.generated_tests = None
            st.session_state.test_results = None

            package_detector = PackageDetector()
            missing_packages = package_detector.get_missing_packages()

            if missing_packages:
                st.warning(f"Required packages: {', '.join(missing_packages)}")
            
            with st.spinner("Generating tests..."):
                try:
                    generator = TestGenerator(api_key)
                    results = generator.process_code(st.session_state.code_content, "uploaded_code.py")
                    if results:
                        st.session_state.generated_tests = results
                        st.success("Tests generated successfully!")
                    else:
                        st.error("Failed to generate tests")
                except Exception as e:
                    logger.error(f"Error generating tests: {e}")
                    st.error(f"Error: {str(e)}")

    with tab2:
        if st.session_state.generated_tests:
            st.header("Generated Test Cases")
            
            with st.expander("Test Cases (JSON)", expanded=True):
                st.json(st.session_state.generated_tests['test_cases'])
            
            with st.expander("Generated Unittest Code", expanded=True):
                st.code(st.session_state.generated_tests['unittest_code'], language="python")
            
            if st.button("Run Tests"):
                with st.spinner("Running tests..."):
                    try:
                        temp_dir, code_path = save_uploaded_code(st.session_state.code_content)
                        if not temp_dir or not code_path:
                            st.error("Failed to save code file")
                            return

                        test_path = os.path.join(temp_dir, "test_uploaded_code.py")
                        with open(test_path, "w") as f:
                            f.write(st.session_state.generated_tests['unittest_code'])
                        
                        init_path = os.path.join(temp_dir, "__init__.py")
                        with open(init_path, "w") as f:
                            f.write("")
                        
                        generator = TestGenerator(api_key)
                        results = run_unittest_file(
                            test_path,
                            generator,
                            st.session_state.code_content,
                            temp_dir
                        )
                        
                        if results:
                            st.session_state.test_results = results
                            st.success("Tests completed!")
                        
                    except Exception as e:
                        logger.error(f"Error running tests: {e}")
                        st.error(f"Error running tests: {e}")

    with tab3:
        if st.session_state.test_results:
            st.header("Test Results")
        
            # Raw test output in expander
            with st.expander("Raw Test Output", expanded=False):
                st.text(st.session_state.test_results['output'])
        
            # Display formatted feedback
            if st.session_state.test_results.get('feedback'):
                display_feedback(st.session_state.test_results['feedback'])
            else:
                st.error("No feedback available")

if __name__ == "__main__":
    main()