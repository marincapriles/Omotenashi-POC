#!/usr/bin/env python3
"""Fix import paths after project reorganization."""

import os
import re

# Import mappings
IMPORT_FIXES = [
    # src/api/main.py imports
    ('from config import', 'from src.api.config import'),
    ('from prompts import', 'from src.agents.prompts import'),
    ('from tools import', 'from src.agents.tools import'),
    
    # Test file imports - they need to go up directories
    ('import tools', 'import sys\nsys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))\nfrom src.agents import tools'),
    ('import prompts', 'from src.agents import prompts'),
    ('import main', 'from src.api import main'),
    ('from main import', 'from src.api.main import'),
]

def fix_imports_in_file(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        for old_import, new_import in IMPORT_FIXES:
            if old_import in content:
                content = content.replace(old_import, new_import)
                print(f"  Fixed: {old_import} -> {new_import}")
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✓ Updated {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to fix all imports."""
    print("Fixing imports after project reorganization...\n")
    
    files_to_fix = [
        'src/api/main.py',
        'src/api/config.py',
        'src/agents/tools.py',
        'src/agents/prompts.py',
        'tests/evaluation/comprehensive_evaluation.py',
        'tests/evaluation/comprehensive_guest_journey_evaluation.py',
        'tests/evaluation/evaluation.py',
        'tests/evaluation/evaluation_multilingual.py',
        'tests/evaluation/fixed_tool_evaluation.py',
        'tests/evaluation/tool_evaluation.py',
        'tests/unit/test_simple_tools.py',
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"\nChecking {file_path}...")
            if fix_imports_in_file(file_path):
                fixed_count += 1
        else:
            print(f"✗ File not found: {file_path}")
    
    print(f"\n✅ Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()