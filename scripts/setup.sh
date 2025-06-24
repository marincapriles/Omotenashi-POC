#!/bin/bash
# Setup script for Omotenashi POC

echo "Setting up Omotenashi POC development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r config/requirements.txt

# Setup environment variables
if [ ! -f .env ]; then
    cp config/.env.example .env
    echo "✓ Created .env file - please update with your values"
fi

# Initialize database
echo "Initializing database..."
python data/migrations/migration_strategy.py

echo "✓ Setup complete! Run 'source venv/bin/activate' to activate the virtual environment."
