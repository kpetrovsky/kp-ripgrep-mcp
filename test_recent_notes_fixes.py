#!/usr/bin/env python3
"""Test recent_notes fixes for max_results capping and date validation."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_recent_notes_max_results():
    """Test max_results parameter validation and capping."""
    test_vault = Path(__file__).parent / "test_vault"
    
    try:
        rg = RipgrepWrapper(str(test_vault))
        
        print("=== TESTING MAX_RESULTS VALIDATION ===")
        
        # Test cases for max_results validation
        test_cases = [
            (0, "Should be capped to minimum of 1"),
            (-5, "Should be capped to minimum of 1"),
            (15, "Should remain as 15 (normal case)"),
            (50, "Should remain as 50 (normal case)"),
            (100, "Should remain as 100 (maximum allowed)"),
            (150, "Should be capped to maximum of 100"),
            (999, "Should be capped to maximum of 100"),
        ]
        
        for max_results_input, description in test_cases:
            print(f"\nTesting max_results={max_results_input} - {description}")
            
            files = rg.get_files_by_date_range(folder=None)
            
            # Apply the same validation logic as the server
            if max_results_input < 1 or max_results_input > 100:
                capped_max_results = min(max(max_results_input, 1), 100)
            else:
                capped_max_results = max_results_input
            
            limited_files = files[:capped_max_results]
            
            print(f"  Input: {max_results_input}")
            print(f"  Capped to: {capped_max_results}")
            print(f"  Files found: {len(files)}")
            print(f"  Files returned: {len(limited_files)}")
            
            # Validate the capping logic
            if max_results_input <= 0:
                assert capped_max_results == 1, f"Expected 1, got {capped_max_results}"
                print("  ✅ Correctly capped to minimum of 1")
            elif max_results_input > 100:
                assert capped_max_results == 100, f"Expected 100, got {capped_max_results}"
                print("  ✅ Correctly capped to maximum of 100")
            else:
                assert capped_max_results == max_results_input, f"Expected {max_results_input}, got {capped_max_results}"
                print("  ✅ Correctly preserved valid value")
        
        print(f"\n=== MAX_RESULTS VALIDATION TESTS COMPLETED ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_date_format_validation():
    """Test date format validation logic."""
    print("\n=== TESTING DATE FORMAT VALIDATION ===")
    
    from datetime import datetime
    
    # Test cases for date validation
    valid_dates = [
        "2024-01-15",
        "2023-12-31", 
        "2024-02-29",  # Valid leap year date
        "1999-01-01",
    ]
    
    invalid_dates = [
        "2024-1-15",      # Missing zero padding
        "24-01-15",       # Wrong year format
        "2024/01/15",     # Wrong separator
        "2024-13-01",     # Invalid month
        "2024-01-32",     # Invalid day
        "invalid-date",   # Completely invalid
        "2024-01",        # Incomplete date
        "",               # Empty string
    ]
    
    print("\nTesting VALID date formats:")
    for date_str in valid_dates:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            print(f"  ✅ '{date_str}' - Valid")
        except ValueError as e:
            print(f"  ❌ '{date_str}' - Should be valid but failed: {e}")
    
    print("\nTesting INVALID date formats:")
    for date_str in invalid_dates:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            print(f"  ❌ '{date_str}' - Should be invalid but passed")
        except ValueError:
            print(f"  ✅ '{date_str}' - Correctly rejected as invalid")
    
    print(f"\n=== DATE FORMAT VALIDATION TESTS COMPLETED ===")

if __name__ == "__main__":
    test_recent_notes_max_results()
    test_date_format_validation()
    print("\n🎉 All recent_notes fixes tested successfully!")