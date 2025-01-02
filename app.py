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

def init_session_state():
    """Initialize session state variables"""
    if 'test_results' not in st.session_state:
        st.session_state.test_results = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    if 'code_content' not in st.session_state:
        st.session_state.code_content = None
    if 'generated_tests' not in st.session_state:
        st.session_state.generated_tests = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None

def generate_basic_feedback(test_output: str) -> dict:
    """Generate basic feedback when AI generation fails"""
    # Parse test results
    total_tests = len(re.findall(r'test_\w+', test_output))
    passed = len(re.findall(r' \.\.\. ok', test_output))
    failed = len(re.findall(r' \.\.\. FAIL', test_output))
    errors = len(re.findall(r' \.\.\. ERROR', test_output))
    
    return {
        "score": round(5.0 * (passed / total_tests if total_tests > 0 else 0), 1),
        "summary": {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors
        },
        "code_quality": {
            "complexity": "medium",
            "maintainability": "fair",
            "test_coverage": f"{(passed/total_tests*100 if total_tests > 0 else 0):.1f}%",
            "best_practices": ["Basic tests implemented"],
            "areas_of_concern": ["Limited test coverage"]
        },
        "detailed_feedback": {
            "strengths": ["Basic functionality tested"],
            "weaknesses": ["Limited edge case testing"],
            "recommendations": ["Add more comprehensive tests"]
        },
        "test_quality": {
            "coverage_assessment": "Basic test coverage achieved",
            "edge_cases": "Limited edge case testing",
            "assertion_quality": "Basic assertions implemented"
        },
        "security_considerations": [
            "No security tests implemented"
        ],
        "performance_insights": {
            "efficiency": "fair",
            "bottlenecks": ["Not analyzed"],
            "optimization_suggestions": ["Implement performance testing"]
        }
    }

def save_uploaded_code(code_content):
    """Save the code to a temporary file and return the file path"""
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        st.session_state.temp_dir = temp_dir
        
        # Save the code file
        code_path = os.path.join(temp_dir, "uploaded_code.py")
        with open(code_path, "w") as f:
            f.write(code_content)
        
        return temp_dir, code_path
    except Exception as e:
        st.error(f"Error saving code: {e}")
        return None, None

def run_unittest_file(unittest_path: str, generator: TestGenerator, original_code: str, code_dir: str) -> dict:
    """Run the generated unittest file and return the test results and output"""
    try:
        # Create containers for status updates
        status_container = st.empty()
        progress_bar = st.progress(0)
        debug_container = st.empty()
        
        def update_status(message: str, progress: int, is_debug: bool = False):
            """Update status with progress"""
            status_container.text(message)
            progress_bar.progress(progress)
            if is_debug:
                debug_container.info(message)

        # Initialize test environment
        update_status("Setting up test environment...", 10)
        
        # Get the directory and file name
        directory = os.path.dirname(unittest_path)
        file_name = os.path.basename(unittest_path)
        module_name = os.path.splitext(file_name)[0]

        # Add the code directory to Python path
        if code_dir not in sys.path:
            sys.path.insert(0, code_dir)
        update_status("Added code directory to Python path", 20, True)

        # Add the test directory to Python path
        if directory not in sys.path:
            sys.path.insert(0, directory)
        update_status("Added test directory to Python path", 30, True)

        # Import the test module
        update_status("Importing test module...", 40)
        try:
            spec = importlib.util.spec_from_file_location(module_name, unittest_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            update_status("Test module imported successfully", 50, True)
        except Exception as e:
            st.error(f"Failed to import test module: {e}")
            raise

        # Create test suite and runner
        update_status("Setting up test suite...", 60)
        try:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            update_status("Test suite created", 65, True)
        except Exception as e:
            st.error(f"Failed to create test suite: {e}")
            raise

        # Capture test output
        update_status("Running tests...", 70)
        output_stream = StringIO()
        runner = unittest.TextTestRunner(stream=output_stream, verbosity=2)

        # Run tests
        try:
            result = runner.run(suite)
            test_output = output_stream.getvalue()
            update_status("Tests completed", 80, True)
            
            # Display immediate test results
            st.write("\n=== Test Execution Summary ===")
            st.write(f"Tests Run: {result.testsRun}")
            st.write(f"Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
            st.write(f"Tests Failed: {len(result.failures)}")
            st.write(f"Test Errors: {len(result.errors)}")
            
            if result.failures:
                st.error("Failed Tests:")
                for failure in result.failures:
                    st.write(f"- {failure[0]}")
                    with st.expander("Show Error Details"):
                        st.code(failure[1])
            
            if result.errors:
                st.error("Test Errors:")
                for error in result.errors:
                    st.write(f"- {error[0]}")
                    with st.expander("Show Error Details"):
                        st.code(error[1])
                        
        except Exception as e:
            st.error(f"Error running tests: {e}")
            raise

        # Generate feedback
        update_status("Generating feedback...", 85)
        try:
            with st.spinner("Analyzing test results..."):
                feedback = generator.generate_feedback(test_output, original_code)
                
                # Show feedback generation method
                if 'ai_generated' in feedback and feedback['ai_generated']:
                    st.success("✨ Using AI-generated feedback")
                else:
                    st.info("📊 Using calculated feedback")
                
                update_status("Feedback generated", 90, True)
        except Exception as e:
            st.error(f"Error generating feedback: {e}")
            raise

        # Save results
        update_status("Saving results...", 95)
        try:
            # Save test output
            output_file = os.path.join(directory, f"{module_name}_output.txt")
            with open(output_file, 'w') as f:
                f.write(test_output)
            
            # Save feedback
            feedback_file = os.path.join(directory, f"{module_name}_feedback.json")
            with open(feedback_file, 'w') as f:
                json.dump(feedback, f, indent=2)
            
            update_status("Results saved", 100, True)
            
            # Show file locations
            st.success(f"Test output saved to: {output_file}")
            st.success(f"Feedback saved to: {feedback_file}")
        except Exception as e:
            st.warning(f"Error saving results: {e}")

        # Clean up progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_container.empty()
        debug_container.empty()

        # Return results
        return {
            'result': result,
            'output': test_output,
            'feedback': feedback,
            'success': len(result.failures) == 0 and len(result.errors) == 0,
            'files': {
                'output': output_file,
                'feedback': feedback_file
            }
        }

    except Exception as e:
        st.error(f"Error in test execution: {e}")
        st.exception(e)  # This will show the full traceback
        return None
    finally:
        # Ensure progress bar is cleared even if there's an error
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_container' in locals():
            status_container.empty()
        if 'debug_container' in locals():
            debug_container.empty()
            
def display_feedback(feedback):
    """Display formatted feedback in Streamlit with enhanced styling for both modes"""
    
    # Main header with custom styling
    st.markdown("""
        <h1 style='text-align: center; color: #1E88E5; padding-bottom: 20px;'>
            Evaluation Results
        </h1>
    """, unsafe_allow_html=True)
    
    # Basic Information in a nice container
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Language:** {feedback['language']}")
        with col2:
            # Score with color based on value
            score = feedback['score']
            color = '#00C853' if score >= 4 else '#FFB300' if score >= 3 else '#E53935'
            st.markdown(
                f"**Score:** <span style='color: {color}; font-size: 18px;'>"
                f"{score:.1f}/5.0</span>",
                unsafe_allow_html=True
            )
    
    # Scoring Explanation with dark mode compatible styling
    st.markdown("### 📝 Scoring Explanation")
    st.markdown(
        f"""<div style='
            background-color: rgba(255, 255, 255, 0.1); 
            color: inherit;
            padding: 15px; 
            border-radius: 5px; 
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;'>
            {feedback['scoring_explanation']}
        </div>""", 
        unsafe_allow_html=True
    )
    
    # Issues Section with better formatting
    if feedback.get('issues'):
        st.markdown("### 🔍 Identified Issues")
        
        for issue in feedback['issues']:
            with st.container():
                # Severity badge with appropriate color
                severity = issue['severity'].lower()
                severity_color = {
                    'low': '#2196F3',      # Blue
                    'medium': '#FF9800',    # Orange
                    'high': '#F44336'       # Red
                }.get(severity, '#757575')  # Grey as default
                
                # Issue header with severity badge
                st.markdown(
                    f"""<div style='margin-bottom: 10px;'>
                        <span style='font-size: 16px; font-weight: bold;'>Issue:</span>
                        <span style='background-color: {severity_color}; color: white; 
                              padding: 2px 8px; border-radius: 10px; margin-left: 10px; 
                              font-size: 12px;'>
                            {issue['severity']}
                        </span>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Issue description
                st.markdown(
                    f"""<div style='margin-left: 20px; margin-bottom: 10px;'>
                        {issue['description']}
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Fix suggestion in a distinct box
                st.markdown(
                    f"""<div style='
                        margin-left: 20px; 
                        padding: 10px; 
                        background-color: rgba(30, 136, 229, 0.1); 
                        border-left: 4px solid #1E88E5; 
                        border-radius: 4px;
                        color: inherit;'>
                        <span style='font-weight: bold;'>Fix:</span> {issue['fix']}
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Separator between issues
                st.markdown("<hr style='margin: 15px 0; opacity: 0.2;'>", unsafe_allow_html=True)

def cleanup():
    """Clean up temporary files"""
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        import shutil
        try:
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        except Exception as e:
            st.warning(f"Error cleaning up temporary files: {e}")

def main():
    st.set_page_config(
        page_title="AI Test Generator",
        page_icon="🧪",
        layout="wide"
    )

    # Initialize session state
    init_session_state()

    # Header
    st.title("🧪 AI Test Generator")
    st.markdown("Generate unit tests for your Python code using AI")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Google API Key", type="password")
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool uses AI to:
        - Generate unit tests
        - Analyze code quality
        - Provide detailed feedback
        - Suggest improvements
        """)

    # Main content
    tab1, tab2, tab3 = st.tabs(["Code Input", "Generated Tests", "Results & Feedback"])

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
                st.session_state.code_content = uploaded_file.getvalue().decode("utf-8")
                st.code(st.session_state.code_content, language="python")
        else:
            st.session_state.code_content = st.text_area(
                "Paste your Python code here",
                height=300,
                help="Enter your Python code here"
            )

        if st.button("Generate Tests", disabled=not (api_key and st.session_state.code_content)):
            with st.spinner("Generating tests..."):
                try:
                    # Initialize test generator
                    generator = TestGenerator(api_key)
                    
                    # Process the code
                    results = generator.process_code(st.session_state.code_content, "uploaded_code.py")
                    
                    if results:
                        st.session_state.generated_tests = results
                        st.success("Tests generated successfully!")
                    else:
                        st.error("Failed to generate tests")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with tab2:
        if st.session_state.generated_tests:
            st.header("Generated Test Cases")
            
            # Display test cases
            with st.expander("Test Cases (JSON)", expanded=True):
                st.json(st.session_state.generated_tests['test_cases'])
            
            # Display unittest code
            with st.expander("Generated Unittest Code", expanded=True):
                st.code(st.session_state.generated_tests['unittest_code'], language="python")
            
            # Run tests button
            if st.button("Run Tests"):
                with st.spinner("Running tests..."):
                    try:
                        # Save the original code
                        temp_dir, code_path = save_uploaded_code(st.session_state.code_content)
                        if not temp_dir or not code_path:
                            st.error("Failed to save code file")
                            return

                        # Save unittest code
                        test_path = os.path.join(temp_dir, "test_uploaded_code.py")
                        with open(test_path, "w") as f:
                            f.write(st.session_state.generated_tests['unittest_code'])
                        
                        # Run tests
                        generator = TestGenerator(api_key)
                        results = run_unittest_file(
                            test_path,
                            generator,
                            st.session_state.code_content,
                            temp_dir
                        )
                        
                        if results:
                            st.session_state.test_results = results
                            st.success("Tests completed successfully!")
                        
                    except Exception as e:
                        st.error(f"Error running tests: {e}")
                        st.exception(e)  # This will show the full traceback
                    finally:
                        cleanup()

    with tab3:
        if st.session_state.test_results:
            st.header("Test Results")
            
            # Display test results
            result = st.session_state.test_results['result']
            with st.expander("Test Output", expanded=True):
                st.text(st.session_state.test_results['output'])
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Tests Run", result.testsRun)
            with col2:
                st.metric("Passed", result.testsRun - len(result.failures) - len(result.errors))
            with col3:
                st.metric("Failed", len(result.failures))
            with col4:
                st.metric("Errors", len(result.errors))
            
            # Display feedback
            if st.session_state.test_results['feedback']:
                display_feedback(st.session_state.test_results['feedback'])

if __name__ == "__main__":
    main()