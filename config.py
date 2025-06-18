"""
Configuration settings for the Omotenashi Hotel Concierge API.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')

# Application Configuration
MEMORY_EXPIRY_HOURS: int = int(os.getenv('MEMORY_EXPIRY_HOURS', '1'))
PORT: int = int(os.getenv('PORT', '8000'))

# Validation
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is required. Please set it in your environment variables or .env file."
    ) 