#!/usr/bin/env python3
"""
Claude Multi-Instance Sync Checker
Automated tool to ensure instances stay synchronized
"""

import subprocess
import sys
from datetime import datetime
import json

def check_git_status():
    """Check if there are unsynced changes"""
    try:
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  UNSYNCED: You have uncommitted changes")
            return False
        
        # Check if branch is ahead/behind
        result = subprocess.run(['git', 'status', '-b', '--porcelain'], 
                              capture_output=True, text=True)
        status_line = result.stdout.split('\n')[0]
        if 'ahead' in status_line or 'behind' in status_line:
            print(f"⚠️  SYNC NEEDED: {status_line}")
            return False
            
        print("✅ Git status clean")
        return True
    except subprocess.CalledProcessError:
        print("❌ Git check failed")
        return False

def check_sync_file():
    """Check if CLAUDE_SYNC.md has new decisions"""
    try:
        with open('CLAUDE_SYNC.md', 'r') as f:
            content = f.read()
        
        # Count decision entries
        decisions = content.count('### [DEC-')
        urgent_items = content.count('🚨')
        
        print(f"📋 Found {decisions} decisions, {urgent_items} urgent items")
        
        if urgent_items > 0:
            print("🚨 URGENT ITEMS REQUIRE ATTENTION!")
            return False
            
        return True
    except FileNotFoundError:
        print("❌ CLAUDE_SYNC.md not found - sync required")
        return False

def get_last_sync():
    """Get timestamp of last sync"""
    try:
        result = subprocess.run(['git', 'log', '-1', '--grep=SYNC', '--format=%ct'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            timestamp = int(result.stdout.strip())
            last_sync = datetime.fromtimestamp(timestamp)
            hours_ago = (datetime.now() - last_sync).total_seconds() / 3600
            
            if hours_ago > 24:
                print(f"⚠️  Last sync was {hours_ago:.1f} hours ago")
                return False
            else:
                print(f"✅ Last sync: {hours_ago:.1f} hours ago")
                return True
        else:
            print("⚠️  No sync commits found")
            return False
    except subprocess.CalledProcessError:
        print("❌ Could not check sync history")
        return False

def main():
    """Run comprehensive sync check"""
    print("🔄 Claude Multi-Instance Sync Check")
    print("=" * 40)
    
    checks = [
        ("Git Status", check_git_status),
        ("Sync Decisions", check_sync_file), 
        ("Last Sync Time", get_last_sync)
    ]
    
    all_good = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("✅ ALL CHECKS PASSED - Instances in sync")
        sys.exit(0)
    else:
        print("⚠️  SYNC REQUIRED - Run sync protocol")
        print("\nRecommended actions:")
        print("1. git pull origin claude-migration")
        print("2. Read CLAUDE_SYNC.md for latest decisions")
        print("3. Address any urgent items")
        print("4. Commit your current work")
        sys.exit(1)

if __name__ == "__main__":
    main()