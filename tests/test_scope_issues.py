#!/usr/bin/env python3
"""Test search scope issues with frontmatter_only and content_only."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_search_scopes():
    """Test different search scopes to identify issues."""
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print("=== SEARCH SCOPE TESTING ===")
        
        # Test cases: [query, should_be_in_frontmatter, should_be_in_content]
        test_cases = [
            ("frontmatter-only-word", True, False),  # Only in frontmatter
            ("content-only-word", False, True),      # Only in content  
            ("scope", True, True),                   # In both (file title + content)
            ("testing", True, True),                 # In both (frontmatter + content)
        ]
        
        for query, expect_fm, expect_content in test_cases:
            print(f"\n--- Testing query: '{query}' ---")
            print(f"Expected: frontmatter={expect_fm}, content={expect_content}")
            
            # Test all search scope
            all_results = rg.search_content(query, max_results=10)
            print(f"ALL scope: {len(all_results)} results")
            
            # Test frontmatter_only scope
            fm_results = rg.search_frontmatter_only(query, max_results=10)
            print(f"FRONTMATTER_ONLY: {len(fm_results)} results")
            if expect_fm and len(fm_results) == 0:
                print("  ❌ ISSUE: Expected frontmatter results but got 0")
            elif not expect_fm and len(fm_results) > 0:
                print("  ⚠️  WARNING: Got frontmatter results but didn't expect any")
            elif expect_fm and len(fm_results) > 0:
                print("  ✅ Good: Found expected frontmatter results")
            
            # Test content_only scope  
            content_results = rg.search_content_only(query, max_results=10)
            print(f"CONTENT_ONLY: {len(content_results)} results")
            if expect_content and len(content_results) == 0:
                print("  ❌ ISSUE: Expected content results but got 0")
            elif not expect_content and len(content_results) > 0:
                print("  ⚠️  WARNING: Got content results but didn't expect any")
            elif expect_content and len(content_results) > 0:
                print("  ✅ Good: Found expected content results")
                
        # Test regex patterns
        print(f"\n--- Testing regex patterns ---")
        
        regex_tests = [
            ("test-pattern-\\d+", "Should find test-pattern-789"),
            ("\\[.*\\]", "Should find [bracket-content]"),
            ("\\w+@\\w+\\.com", "Should find test@example.com"),
        ]
        
        for regex, description in regex_tests:
            print(f"\nRegex: {regex} ({description})")
            
            all_results = rg.search_content(regex, max_results=5)
            fm_results = rg.search_frontmatter_only(regex, max_results=5) 
            content_results = rg.search_content_only(regex, max_results=5)
            
            print(f"  ALL: {len(all_results)}, FRONTMATTER: {len(fm_results)}, CONTENT: {len(content_results)}")
            
            if len(all_results) == 0:
                print("  ❌ ISSUE: Regex found no results in any scope")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_scopes()