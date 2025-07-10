#!/usr/bin/env python3
"""Test max_results fix."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_max_results():
    """Test that max_results is respected."""
    # We can't import the server directly due to MCP dependency,
    # but we can test the ripgrep wrapper directly
    from rgrep_mcp.ripgrep import RipgrepWrapper
    
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print("=== MAX RESULTS TEST ===")
        
        # Test with different max_results values
        for max_val in [2, 5, 10]:
            print(f"\nTesting max_results={max_val}:")
            results = rg.search_content("meeting", max_results=max_val)
            print(f"  Requested: {max_val}, Got: {len(results)} results")
            
            if len(results) <= max_val:
                print(f"  ✅ Results within limit")
            else:
                print(f"  ❌ Too many results returned")
                
        # Test the actual server function logic
        print(f"\n=== SERVER LOGIC TEST ===")
        
        # Simulate what server does
        results = rg.search_content("meeting", max_results=100)  # Get many results
        print(f"Raw ripgrep results: {len(results)}")
        
        # Apply server-side limiting
        max_results = 5
        limited_results = results[:max_results] if results else []
        print(f"After server limiting to {max_results}: {len(limited_results)}")
        
        # Show sample results (without frontmatter)
        print(f"\nSample limited results:")
        for i, result in enumerate(limited_results[:3]):
            formatted = {
                "file": result['file'],
                "line_number": result['line_number'],
                "snippet": (result.get('text', '') or '').strip()
            }
            print(f"  {i+1}. {formatted}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_max_results()