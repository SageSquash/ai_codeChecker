import os
import sys

def create_project_structure():
    # Project structure definition
    structure = {
        'src': {
            '__init__.py': '',
            'test_generator.py': '',
            'code_analyzer.py': '',
            'test_case_generator.py': '',
            'unittest_generator.py': '',
            'result_analyzer.py': ''
        },
        'tests': {
            '__init__.py': '',
            'test_test_generator.py': '',
            'test_code_analyzer.py': '',
            'test_case_generator.py': '',
            'test_unittest_generator.py': '',
            'test_result_analyzer.py': ''
        },
        'config': {
            'config.py': ''
        },
        'utils': {
            '__init__.py': '',
            'helpers.py': ''
        }
    }

    # Create requirements.txt content
    requirements_content = '''google-generativeai
pytest
typing'''

    # Create setup.py content
    setup_content = '''from setuptools import setup, find_packages

setup(
    name="test-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "pytest",
        "typing",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A test generator using Google's Generative AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test-generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)'''

    # Create main.py content
    main_content = '''if __name__ == "__main__":
    print("Test Generator Application")
    # Add your main application logic here
'''

    def create_directory_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            
            # Create directory
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"Created directory: {path}")

            # If content is a dictionary, recurse
            if isinstance(content, dict):
                for file_name, file_content in content.items():
                    file_path = os.path.join(path, file_name)
                    with open(file_path, 'w') as f:
                        f.write(file_content)
                    print(f"Created file: {file_path}")
            else:
                # Create file
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Created file: {path}")

    # Get current directory
    current_dir = os.getcwd()
    project_name = 'test_generator_project'
    project_path = os.path.join(current_dir, project_name)

    # Create project directory
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print(f"Created project directory: {project_path}")

    # Create directory structure
    create_directory_structure(project_path, structure)

    # Create additional files in project root
    with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)
    print(f"Created file: {os.path.join(project_path, 'requirements.txt')}")

    with open(os.path.join(project_path, 'setup.py'), 'w') as f:
        f.write(setup_content)
    print(f"Created file: {os.path.join(project_path, 'setup.py')}")

    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(main_content)
    print(f"Created file: {os.path.join(project_path, 'main.py')}")

    print("\nProject structure created successfully!")
    print(f"Project location: {project_path}")

if __name__ == "__main__":
    try:
        create_project_structure()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)