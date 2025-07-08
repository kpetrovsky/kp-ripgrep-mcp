#!/usr/bin/env python3
"""Simple test to isolate ripgrep issues."""

import subprocess
import json
from pathlib import Path

def test_simple_ripgrep():
    """Test simplified ripgrep commands."""
    test_vault = Path(__file__).parent / "test_vault"
    vault_win = str(test_vault).replace("/mnt/c", "C:").replace("/", "\\")
    
    print("=== SIMPLIFIED RIPGREP TESTS ===")
    
    # Test 1: Most basic search
    print("\n1. Basic search without any flags:")
    cmd1 = ["rg.exe", "meeting", vault_win]
    print(f"Command: {' '.join(cmd1)}")
    try:
        result = subprocess.run(cmd1, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        match_count = len(result.stdout.split('\n')) if result.stdout else 0
        print(f"Matches found: {match_count}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: JSON output only
    print("\n2. JSON output only:")
    cmd2 = ["rg.exe", "--json", "meeting", vault_win]
    print(f"Command: {' '.join(cmd2)}")
    try:
        result = subprocess.run(cmd2, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            lines = [line for line in result.stdout.split('\n') if line.strip()]
            matches = []
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'match':
                        matches.append(data)
                except:
                    continue
            print(f"JSON matches found: {len(matches)}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: With file glob
    print("\n3. With markdown file glob:")
    cmd3 = ["rg.exe", "--json", "--glob", "*.md", "meeting", vault_win]
    print(f"Command: {' '.join(cmd3)}")
    try:
        result = subprocess.run(cmd3, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            lines = [line for line in result.stdout.split('\n') if line.strip()]
            matches = []
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'match':
                        matches.append(data)
                except:
                    continue
            print(f"JSON matches found: {len(matches)}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 4: Our current complex command
    print("\n4. Current complex command:")
    cmd4 = ["rg.exe", "--ignore-case", "--json", "--context", "1", "--max-count", "15", 
            "--glob", "*.md", "--glob", "!.obsidian/**", "meeting", vault_win]
    print(f"Command: {' '.join(cmd4)}")
    try:
        result = subprocess.run(cmd4, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            lines = [line for line in result.stdout.split('\n') if line.strip()]
            matches = []
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'match':
                        matches.append(data)
                except:
                    continue
            print(f"JSON matches found: {len(matches)}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_simple_ripgrep()