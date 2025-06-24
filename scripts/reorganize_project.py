#!/usr/bin/env python3
"""
Reorganize Omotenashi POC project structure for better external digestibility.
Run with: python reorganize_project.py
"""

import os
import shutil
from pathlib import Path

# File mapping: current location -> new location
FILE_MAPPING = {
    # Source code files
    'main.py': 'src/api/main.py',
    'config.py': 'src/api/config.py',
    'tools.py': 'src/agents/tools.py',
    'prompts.py': 'src/agents/prompts.py',
    
    # Infrastructure files
    'Dockerfile': 'infrastructure/docker/Dockerfile',
    'docker-compose.yml': 'infrastructure/docker/docker-compose.yml',
    'nginx.conf': 'infrastructure/nginx/nginx.conf',
    'database_schema.sql': 'data/migrations/001_initial_schema.sql',
    'migration_strategy.py': 'data/migrations/migration_strategy.py',
    
    # Data files
    'guests.json': 'data/demo/guests.json',
    'bookings.json': 'data/demo/bookings.json',
    'villa_azul.txt': 'data/demo/villa_azul.txt',
    'chroma_db': 'data/vector_store/chroma_db',
    
    # Frontend files
    'static/index.html': 'frontend/index.html',
    'serve_frontend.py': 'frontend/serve_frontend.py',
    
    # Test and evaluation files
    'comprehensive_evaluation.py': 'tests/evaluation/comprehensive_evaluation.py',
    'comprehensive_guest_journey_evaluation.py': 'tests/evaluation/comprehensive_guest_journey_evaluation.py',
    'fixed_tool_evaluation.py': 'tests/evaluation/fixed_tool_evaluation.py',
    'evaluation.py': 'tests/evaluation/evaluation.py',
    'evaluation_multilingual.py': 'tests/evaluation/evaluation_multilingual.py',
    'simple_tool_test.py': 'tests/unit/test_simple_tools.py',
    'tool_evaluation.py': 'tests/evaluation/tool_evaluation.py',
    'quick_comprehensive_eval.py': 'tests/evaluation/quick_comprehensive_eval.py',
    'quick_eval.py': 'tests/evaluation/quick_eval.py',
    
    # Test results
    'comprehensive_tool_evaluation_results.txt': 'tests/evaluation/results/comprehensive_tool_evaluation_results.txt',
    'comprehensive_guest_journey_results.txt': 'tests/evaluation/results/comprehensive_guest_journey_results.txt',
    'tool_evaluation_results_2025-06-21.txt': 'tests/evaluation/results/tool_evaluation_results_2025-06-21.txt',
    'tool_evaluation_results_2025-06-22.txt': 'tests/evaluation/results/tool_evaluation_results_2025-06-22.txt',
    'claude4_evaluation_real_results.txt': 'tests/evaluation/results/claude4_evaluation_real_results.txt',
    'claude4_evaluation_summary.txt': 'tests/evaluation/results/claude4_evaluation_summary.txt',
    
    # Documentation - Architecture
    'AUTH_API_CONTRACT.md': 'docs/api/AUTH_API_CONTRACT.md',
    'database_schema.sql': 'docs/architecture/DATABASE_SCHEMA.md',
    
    # Documentation - Development
    'GIT_WORKFLOW.md': 'docs/development/GIT_WORKFLOW.md',
    
    # Management - Claude Coordination
    'CLAUDE_SYNC.md': 'management/claude_coordination/CLAUDE_SYNC.md',
    'CONCIERGE_SAN_SYSTEM_INSTRUCTION.md': 'management/claude_coordination/CONCIERGE_SAN_SYSTEM_INSTRUCTION.md',
    'RYOKAN_SYSTEM_INSTRUCTION.md': 'management/claude_coordination/RYOKAN_SYSTEM_INSTRUCTION.md',
    'PROTOCOL_UPDATE_FOR_CONCIERGE_SAN.md': 'management/claude_coordination/PROTOCOL_UPDATE.md',
    
    # Management - Planning
    'CONCIERGE_SAN_PILOT_WORKPLAN.md': 'management/planning/CONCIERGE_SAN_PILOT_WORKPLAN.md',
    'RYOKAN_PILOT_WORKPLAN.md': 'management/planning/RYOKAN_PILOT_WORKPLAN.md',
    'DAILY_PILOT_DASHBOARD.md': 'management/planning/DAILY_PILOT_DASHBOARD.md',
    'HUMAN_DECISIONS.txt': 'management/planning/HUMAN_DECISIONS.txt',
    
    # Management - Analysis
    'CONCIERGE_RYOKAN_COORDINATION_ANALYSIS.md': 'management/analysis/COORDINATION_ANALYSIS.md',
    'tool_expansion_analysis.txt': 'management/analysis/TOOL_EXPANSION_ANALYSIS.txt',
    'guest_centric_tool_expansion_plan.txt': 'management/analysis/guest_centric_tool_expansion_plan.txt',
    
    # Config files
    'requirements.txt': 'config/requirements.txt',
    
    # Keep at root
    'README.md': 'README.md',
    'CLAUDE.md': 'CLAUDE.md',  # Keep for now, might merge into README later
}

# Directories to create
DIRECTORIES = [
    'src/api',
    'src/agents',
    'src/models',
    'src/utils',
    'infrastructure/docker',
    'infrastructure/kubernetes',
    'infrastructure/terraform',
    'infrastructure/nginx',
    'data/demo',
    'data/migrations',
    'data/vector_store',
    'tests/unit',
    'tests/integration',
    'tests/evaluation/results',
    'frontend/static/css',
    'frontend/static/js',
    'frontend/static/img',
    'docs/architecture',
    'docs/api',
    'docs/deployment',
    'docs/development',
    'management/claude_coordination',
    'management/planning',
    'management/analysis',
    'scripts',
    'config',
]

def create_directories():
    """Create all necessary directories."""
    print("Creating directory structure...")
    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if directory.startswith('src/') and not directory.endswith('src'):
            init_file = Path(directory) / '__init__.py'
            init_file.touch(exist_ok=True)
    print("✓ Directory structure created")

def move_files():
    """Move files to their new locations."""
    print("\nMoving files...")
    moved_count = 0
    skipped_count = 0
    
    for old_path, new_path in FILE_MAPPING.items():
        if os.path.exists(old_path):
            # Create parent directory if needed
            Path(new_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file/directory
            try:
                shutil.move(old_path, new_path)
                print(f"✓ Moved {old_path} -> {new_path}")
                moved_count += 1
            except Exception as e:
                print(f"✗ Error moving {old_path}: {e}")
        else:
            skipped_count += 1
    
    print(f"\n✓ Moved {moved_count} files/directories")
    if skipped_count > 0:
        print(f"ℹ Skipped {skipped_count} files (not found)")

def create_additional_files():
    """Create additional files for better structure."""
    print("\nCreating additional files...")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Logs
*.log
server.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Test coverage
htmlcov/
.coverage
.pytest_cache/

# Build
dist/
build/
*.egg-info/
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✓ Created .gitignore")
    
    # Create setup.sh script
    setup_script = """#!/bin/bash
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
"""
    
    with open('scripts/setup.sh', 'w') as f:
        f.write(setup_script)
    os.chmod('scripts/setup.sh', 0o755)
    print("✓ Created scripts/setup.sh")
    
    # Create .env.example
    env_example = """# Omotenashi POC Environment Variables

# API Keys
ANTHROPIC_API_KEY=your-api-key-here
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/omotenashi
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
DEBUG=true

# Security
JWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Server
PORT=8000
HOST=0.0.0.0
"""
    
    with open('config/.env.example', 'w') as f:
        f.write(env_example)
    print("✓ Created config/.env.example")

def update_imports():
    """Update import statements in Python files."""
    print("\nUpdating imports...")
    # This would need to be implemented based on actual import patterns
    print("ℹ Import updates need to be done manually")

def main():
    """Main execution function."""
    print("🏨 Omotenashi POC Project Reorganization")
    print("=" * 50)
    
    # Auto-proceed for Claude execution
    print("\nProceeding with reorganization...")
    
    # Create backup first
    print("\nCreating backup...")
    backup_dir = f"backup_{Path.cwd().name}_{os.getpid()}"
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns('venv', '__pycache__', '.git'))
    print(f"✓ Backup created at: {backup_dir}")
    
    # Perform reorganization
    create_directories()
    move_files()
    create_additional_files()
    update_imports()
    
    print("\n✅ Reorganization complete!")
    print(f"Backup saved at: {backup_dir}")
    print("\nNext steps:")
    print("1. Review the new structure")
    print("2. Update any remaining import statements")
    print("3. Test that everything still works")
    print("4. Commit the changes")
    print("5. Delete the backup directory when satisfied")

if __name__ == "__main__":
    main()