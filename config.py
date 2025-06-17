from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Debug logging
print("Current working directory:", os.getcwd())
print("Environment variables:", os.environ.get('OPENAI_API_KEY'))
print("API Key loaded:", bool(OPENAI_API_KEY))

# Validate that the API key exists
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables") 