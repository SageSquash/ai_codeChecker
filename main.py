import os
import json
import unittest
import importlib.util
from dotenv import load_dotenv
from src.test_generator import TestGenerator
from config.config import Config

def run_unittest_file(unittest_path: str, generator: TestGenerator, original_code: str) -> tuple:
    """
    Run the generated unittest file and return the test results and output
    """
    try:
        # Get the directory and file name
        directory = os.path.dirname(unittest_path)
        file_name = os.path.basename(unittest_path)
        module_name = os.path.splitext(file_name)[0]

        # Add the directory to Python path
        import sys
        if directory not in sys.path:
            sys.path.insert(0, directory)

        # Import the test module
        spec = importlib.util.spec_from_file_location(module_name, unittest_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        # Create test suite and runner
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Capture test output
        from io import StringIO
        output_stream = StringIO()
        runner = unittest.TextTestRunner(stream=output_stream, verbosity=2)

        print("\n=== Running Tests ===")
        result = runner.run(suite)
        test_output = output_stream.getvalue()
        
        # Generate feedback
        print("\n=== Generating Feedback ===")
        feedback = generator.generate_feedback(test_output, original_code)
        
        # Print test summary
        print("\n=== Test Summary ===")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        # Print feedback
        print("\n=== Code Analysis Feedback ===")
        print(f"Overall Score: {feedback['score']}/5.0")
        print(f"Code Quality: {feedback['code_quality']['complexity']} complexity, {feedback['code_quality']['maintainability']} maintainability")
        print(f"Test Coverage: {feedback['code_quality']['test_coverage']}")
        
        print("\nStrengths:")
        for strength in feedback['detailed_feedback']['strengths']:
            print(f"✓ {strength}")
        
        print("\nAreas for Improvement:")
        for weakness in feedback['detailed_feedback']['weaknesses']:
            print(f"! {weakness}")
        
        print("\nRecommendations:")
        for rec in feedback['detailed_feedback']['recommendations']:
            print(f"→ {rec}")
        
        # Save feedback to file
        feedback_path = os.path.join(directory, f"{module_name}_feedback.json")
        with open(feedback_path, 'w') as f:
            json.dump(feedback, f, indent=2)
        print(f"\n✓ Detailed feedback saved to: {feedback_path}")
        
        return len(result.failures) == 0 and len(result.errors) == 0, feedback

    except Exception as e:
        print(f"Error running tests: {e}")
        return False, None

def main():
    # Load environment variables
    load_dotenv()
    
    print("\n=== Test Generator Starting ===")
    
    # Initialize configuration
    try:
        Config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return

    # Create necessary directories
    Config.create_directories()
    print("✓ Directories created")

    # Initialize test generator
    print(f"\nInitializing test generator with API key: {Config.GOOGLE_API_KEY[:8]}...")
    generator = TestGenerator(Config.GOOGLE_API_KEY)
    print("✓ Test generator initialized")

    # Get input file
    file_path = input("\nEnter path to Python file: ")
    print(f"\nReading file: {file_path}")
    
    # Read and process code
    code = generator.read_python_file(file_path)
    if not code:
        return
    print("✓ Code read successfully")
    print("\nCode content:")
    print("-" * 40)
    print(code)
    print("-" * 40)

    # Process the code
    print("\nGenerating tests...")
    results = generator.process_code(code, file_path)
    
    # Output results
    if results:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = Config.OUTPUT_DIR
        
        # Save test cases
        test_cases_path = os.path.join(output_dir, f"{base_name}_test_cases.json")
        with open(test_cases_path, 'w') as f:
            json.dump(results['test_cases'], f, indent=4)
        print(f"✓ Test cases saved to: {test_cases_path}")
        
        # Save unittest code
        unittest_path = os.path.join(output_dir, f"{base_name}_test.py")
        with open(unittest_path, 'w') as f:
            f.write(results['unittest_code'])
        print(f"✓ Unittest code saved to: {unittest_path}")
        
        print("\n=== Generated Files Content ===")
        print("\nTest Cases (JSON):")
        print(json.dumps(results['test_cases'], indent=2))
        print("\nUnittest Code:")
        print(results['unittest_code'])
        
        print(f"\n✓ All files generated in {output_dir}/")
        
        # Run tests and get feedback
        success, feedback = run_unittest_file(unittest_path, generator, code)
        
        # Print final status
        print("\n=== Final Status ===")
        if success:
            print("✓ All tests passed successfully!")
        else:
            print("✗ Some tests failed or had errors")
        
        if feedback:
            print(f"\nFinal Score: {feedback['score']}/5.0")
            print("\nKey Recommendations:")
            for rec in feedback['detailed_feedback']['recommendations'][:3]:
                print(f"• {rec}")
            
    else:
        print("✗ No results generated")

    print("\n=== Test Generator Completed ===")

if __name__ == "__main__":
    main()