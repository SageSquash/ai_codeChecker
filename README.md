<img width="750" alt="Screenshot 2025-01-05 at 7 59 35 PM" src="https://github.com/user-attachments/assets/7e772eb4-fa01-4c67-a20c-59ec496a15f8" />
<img width="750" alt="Screenshot 2025-01-05 at 7 59 56 PM" src="https://github.com/user-attachments/assets/52770134-91dd-45a8-8a94-d8ca9f092f86" />

# AI Code Checker

AI Code Checker is an innovative tool that leverages **Large Language Models (LLMs)** to provide intelligent code analysis and feedback. By combining **automated testing** with **AI-powered code review**, the tool delivers comprehensive, human-like feedback on code quality, implementation, and potential improvements.

## Key Features

- **Automated Test Execution and Analysis**: Run tests automatically and analyze results seamlessly.
- **AI-Powered Code Quality Assessment**: Utilize state-of-the-art LLMs to evaluate code quality and provide detailed insights.
- **Detailed Scoring with Explanations**: Receive a comprehensive score breakdown with clear, actionable explanations.
- **Intelligent Issue Detection and Prioritization**: Identify and prioritize potential issues in your codebase.
- **Actionable Improvement Suggestions**: Get tailored suggestions with severity levels to improve your code.
- **Beautiful, Responsive UI**: Built with **Streamlit**, the tool offers a sleek and user-friendly interface.
- **Light and Dark Mode Support**: Choose between light and dark themes for a comfortable user experience.
- **Real-Time Feedback Generation**: Instantly generate feedback as you write or upload code.

### New Features

- **Dynamic Package Management**: Automatically detects and installs required packages for testing.
- **Secure Docker Integration**: Runs tests in isolated containers with proper permissions.
- **Smart Import Detection**: Recognizes common package aliases (e.g., 'np' for numpy).
- **Enhanced Error Handling**: Provides clear feedback for setup and execution issues.
- **Structured Test Results**: Organized display of test outcomes with severity indicators.
- **Expanded Test Coverage**: Support for various Python testing frameworks.
- **Performance Optimization**: Efficient test execution with parallel processing.
- **Clean Output Format**: Filtered test results without system warnings.

## Technical Stack

- **Programming Language**: Python
- **UI Framework**: Streamlit
- **AI Backend**: Google's Generative AI for intelligent analysis
- **Testing Framework**: Custom test execution framework with unittest integration
- **Container Technology**: Docker for isolated test environments
- **Package Management**: Dynamic dependency detection and installation
- **Security**: Non-root user execution in containers
- **Parsing**: Advanced regex for test result analysis
- **Feedback System**: JSON-based structured feedback

## System Requirements

- Python 3.9 or higher
- Docker installed and running
- Internet connection for AI analysis
- Sufficient disk space for Docker images

## Installation

```bash
# Clone the repository
https://github.com/SageSquash/ai_codeChecker.git

# Navigate to project directory
cd ai-code-checker

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt

# Build Docker image
docker build -t python-test-runner:v1 .
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Configure your Google API key in the sidebar
3. Choose input method (file upload or paste code)
4. Click "Generate Tests" to create test cases
5. Run tests to get comprehensive analysis

## Features in Detail

### Dynamic Package Management
- Automatic detection of required packages
- Support for common package aliases
- Seamless installation in test environment

### Secure Testing Environment
- Isolated Docker containers
- Non-root user execution
- Clean environment for each test run

### Comprehensive Results
- Detailed test outcomes
- Pass/fail metrics
- Code quality insights
- Severity-based issue categorization

### AI-Powered Analysis
- Context-aware feedback
- Pattern recognition
- Best practice suggestions
- Performance insights

## Why AI Code Checker?

This project showcases the practical implementation of **AI/LLM technology** in software development workflows. It demonstrates both **technical expertise** and a deep understanding of **real-world developer needs**, making it an invaluable tool for improving code quality and developer productivity.

### Key Benefits

- **Automated Dependency Management**: No manual package installation required
- **Secure Execution**: Isolated testing environment for safety
- **Comprehensive Analysis**: Combined automated and AI-powered testing
- **User-Friendly Interface**: Clear, organized result presentation
- **Actionable Insights**: Practical improvement suggestions

<img width="1472" alt="Screenshot 2025-01-04 at 8 54 28 PM" src="https://github.com/user-attachments/assets/9ae8dbdd-b0f6-4d8e-ab35-c68b53c92790" />

## Contributing

Contributions are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
