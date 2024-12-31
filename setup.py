from setuptools import setup, find_packages

setup(
    name="test-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "pytest",
        "typing",
    ],
    author="Aditya Raj",
    author_email="adityacool2134@gmail.com",
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
)