import os
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Config:
    """Configuration settings for the application"""
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    MODEL_NAME: str = 'gemini-2.0-flash-exp'
    
    # File paths and directories
    OUTPUT_DIR: str = 'output'
    TEST_DIR: str = 'tests'
    
    # Test generation settings
    MAX_TEST_CASES: int = 10
    INCLUDE_EDGE_CASES: bool = True
    INCLUDE_ERROR_CASES: bool = True
    
    # Analysis settings
    MIN_TEST_COVERAGE: float = 80.0
    COMPLEXITY_THRESHOLD: Dict[str, int] = field(default_factory=lambda: {
        'low': 5,
        'medium': 10,
        'high': 15
    })

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        return True

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEST_DIR, exist_ok=True)