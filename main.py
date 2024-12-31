import os
import json
from dotenv import load_dotenv
from src.test_generator import TestGenerator
from config.config import Config

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
    results = generator.process_code(code, file_path)  # Pass both code and file_path
    
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
        
        print("\nTo run tests, use:")
        print(f"python -m unittest {unittest_path}")
    else:
        print("✗ No results generated")

    print("\n=== Test Generator Completed ===")

if __name__ == "__main__":
    main()