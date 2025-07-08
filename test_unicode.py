#!/usr/bin/env python3
"""Test Unicode handling after encoding fix."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_unicode_search():
    """Test search with Unicode characters."""
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print("=== UNICODE SEARCH TESTS ===")
        
        # Test 1: Search for term that should find Unicode content
        print(f"\n1. Searching for 'Projects'...")
        results = rg.search_content("Projects", max_results=10)
        print(f"Results: {len(results)} matches")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result['file']}:{result['line_number']} - {result['text'][:60]}...")
        
        # Test 2: Search for Unicode characters directly
        print(f"\n2. Searching for 'café'...")
        results = rg.search_content("café", max_results=5)
        print(f"Results: {len(results)} matches")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['file']}:{result['line_number']} - {result['text'][:60]}...")
        
        # Test 3: Search for smart quotes
        print(f"\n3. Searching for smart quotes...")
        results = rg.search_content('"Smart', max_results=5)
        print(f"Results: {len(results)} matches")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['file']}:{result['line_number']} - {result['text'][:60]}...")
        
        print("\n✅ Unicode tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unicode_search()