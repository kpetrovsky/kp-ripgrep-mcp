#!/usr/bin/env python3
"""Test smart context functionality for frontmatter properties and content headings."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_smart_context():
    """Test smart context detection for frontmatter properties and content headings."""
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print("=== SMART CONTEXT TESTING ===")
        
        # Test cases for frontmatter context
        print("\n--- Testing Frontmatter Property Context ---")
        
        frontmatter_tests = [
            ("ProjectAlpha", "mentioned_projects"),  # Should find property name
            ("Balaboom", "mentioned_projects"),     # Should find property name
            ("Alice", "collaborators"),             # Should find property name
            ("Charlie", "assigned_to"),             # Should find property name
            ("SuperProject", "name"),               # Should find immediate property
            ("DevLead", "team_lead"),               # Should find immediate property
            ("Developer1", "developers"),           # Should find immediate property
            ("DeepLink", "deep_reference"),         # Should find immediate property
        ]
        
        for query, expected_property in frontmatter_tests:
            print(f"\nTesting frontmatter query: '{query}' (expect property: {expected_property})")
            
            # Test with smart_context=True
            results_with_context = rg.search_frontmatter_only(query, smart_context=True, max_results=5)
            print(f"  Results with smart_context: {len(results_with_context)}")
            
            if results_with_context:
                for result in results_with_context:
                    print(f"    File: {result['file']}, Line: {result['line_number']}")
                    print(f"    Text: {result['text']}")
                    if 'smart_context' in result:
                        print(f"    Smart Context: {result['smart_context']}")
                        if expected_property in result['smart_context']:
                            print(f"    ✅ Found expected property: {expected_property}")
                        else:
                            print(f"    ❌ Expected property '{expected_property}' not found in context")
                    else:
                        print(f"    ❌ No smart_context field found")
            
            # Test with smart_context=False for comparison
            results_without_context = rg.search_frontmatter_only(query, smart_context=False, max_results=5)
            print(f"  Results without smart_context: {len(results_without_context)}")
            
            if results_without_context:
                for result in results_without_context:
                    if 'smart_context' in result:
                        print(f"    ❌ smart_context field should not be present when disabled")
        
        # Test cases for content heading context
        print("\n--- Testing Content Heading Context ---")
        
        content_tests = [
            ("ProjectAlpha", "Project Overview"),     # Should find heading
            ("ProjectBeta", "Project Overview"),      # Should find heading
            ("Alice", "Team Members"),               # Should find heading
            ("Bob", "Team Members"),                 # Should find heading
            ("Charlie", "Team Members"),             # Should find heading
            ("DevLead", "Team Lead"),                # Should find nested heading
            ("Developer1", "Developers"),            # Should find nested heading
            ("ImportantDoc", "Primary References"),  # Should find nested heading
            ("DeepLink", "Level 3"),                 # Should find deeply nested heading
        ]
        
        for query, expected_heading in content_tests:
            print(f"\nTesting content query: '{query}' (expect heading: {expected_heading})")
            
            # Test with smart_context=True
            results_with_context = rg.search_content_only(query, smart_context=True, max_results=5)
            print(f"  Results with smart_context: {len(results_with_context)}")
            
            if results_with_context:
                for result in results_with_context:
                    print(f"    File: {result['file']}, Line: {result['line_number']}")
                    print(f"    Text: {result['text']}")
                    if 'smart_context' in result:
                        print(f"    Smart Context: {result['smart_context']}")
                        if expected_heading in result['smart_context']:
                            print(f"    ✅ Found expected heading: {expected_heading}")
                        else:
                            print(f"    ❌ Expected heading '{expected_heading}' not found in context")
                    else:
                        print(f"    ❌ No smart_context field found")
        
        # Test mixed search (all content) with smart context
        print("\n--- Testing Mixed Search (All Content) ---")
        
        mixed_tests = [
            ("ProjectAlpha", ["mentioned_projects", "Project Overview"]),  # Both frontmatter and content
            ("Charlie", ["assigned_to", "Team Members"]),                 # Both frontmatter and content
            ("SuperProject", ["name", "Introduction"]),                   # Both frontmatter and content
        ]
        
        for query, expected_contexts in mixed_tests:
            print(f"\nTesting mixed query: '{query}' (expect contexts: {expected_contexts})")
            
            results = rg.search_content(query, smart_context=True, max_results=10)
            print(f"  Results: {len(results)}")
            
            found_contexts = []
            for result in results:
                if 'smart_context' in result:
                    found_contexts.append(result['smart_context'])
                    print(f"    File: {result['file']}, Context: {result['smart_context']}")
            
            for expected in expected_contexts:
                if any(expected in context for context in found_contexts):
                    print(f"    ✅ Found expected context: {expected}")
                else:
                    print(f"    ❌ Expected context '{expected}' not found")
        
        print("\n=== TEST SUMMARY ===")
        print("Smart context testing completed. Check for ✅ and ❌ markers above.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_context()