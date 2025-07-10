#!/usr/bin/env python3
"""Test script to debug search functionality with test vault."""

import sys
import json
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_manual_ripgrep():
    """Test ripgrep manually to see what it should return."""
    print("=== MANUAL RIPGREP TESTS ===")
    
    test_vault = Path(__file__).parent / "test_vault"
    
    # Test basic search
    print(f"\n1. Testing basic 'meeting' search in {test_vault}")
    os.system(f'rg "meeting" "{test_vault}/" || echo "Command failed"')
    
    print(f"\n2. Testing with our parameters:")
    cmd = f'rg --ignore-case --json --context 1 --max-count 15 --glob "*.md" --glob "!.obsidian/**" "meeting" "{test_vault}/"'
    print(f"Command: {cmd}")
    os.system(f'{cmd} || echo "Command failed"')

def test_wrapper():
    """Test our RipgrepWrapper with test vault."""
    print("\n=== WRAPPER TESTS ===")
    
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print(f"\n1. Testing search_content('meeting')...")
        results = rg.search_content("meeting")
        print(f"Results: {len(results)} matches")
        for i, result in enumerate(results[:3]):  # Show first 3
            print(f"  {i+1}. {result['file']}:{result['line_number']} - {result['text'][:50]}...")
        
        print(f"\n2. Testing find_links()...")
        links = rg.find_links()
        print(f"Links: {len(links)} found")
        for i, link in enumerate(links[:3]):  # Show first 3
            print(f"  {i+1}. {link['file']}:{link['line_number']} - {link['link_type']} - {link['url']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_with_server():
    """Test the MCP server functions."""
    print("\n=== SERVER FUNCTION TESTS ===")
    
    # We need to temporarily set the vault path for testing
    import os
    test_vault = Path(__file__).parent / "test_vault"
    os.environ['VAULT_PATH'] = str(test_vault)
    
    try:
        from rgrep_mcp.server import rg_search_notes, rg_search_links
        
        print(f"\n1. Testing rg_search_notes('meeting')...")
        result = rg_search_notes("meeting")
        result_dict = json.loads(result)
        print(f"Total matches: {result_dict.get('total_matches', 0)}")
        
        print(f"\n2. Testing rg_search_links()...")
        result = rg_search_links()
        result_dict = json.loads(result)
        print(f"Total links: {result_dict.get('total_matches', 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting debugging tests...")
    
    test_manual_ripgrep()
    test_wrapper()
    test_with_server()
    
    print("\nDone! Check debug output above.")