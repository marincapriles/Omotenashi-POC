"""
Configuration settings for the Omotenashi Hotel Concierge API.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anthropic Configuration
ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_MODEL: str = os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')

# Application Configuration
MEMORY_EXPIRY_HOURS: int = int(os.getenv('MEMORY_EXPIRY_HOURS', '1'))
PORT: int = int(os.getenv('PORT', '8000'))

# Validation
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY is required. Please set it in your environment variables or .env file."
    ) 