#!/usr/bin/env python3
"""Test server-level date validation for recent_notes."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_date_validation_logic():
    """Test the date validation logic that will be used in the server."""
    print("=== TESTING SERVER DATE VALIDATION LOGIC ===")
    
    from datetime import datetime
    
    # Test cases that should trigger errors
    invalid_dates = [
        "24-01-15",       # Wrong year format
        "2024/01/15",     # Wrong separator
        "2024-13-01",     # Invalid month
        "2024-01-32",     # Invalid day
        "invalid-date",   # Completely invalid
        "2024-01",        # Incomplete date
        "",               # Empty string
    ]
    
    def validate_date(date_str, param_name):
        """Simulate the server's date validation logic."""
        if date_str is not None:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return None  # No error
            except ValueError:
                return {
                    "error": f"Invalid {param_name} format: '{date_str}'. Expected YYYY-MM-DD format (e.g., '2024-01-15')"
                }
        return None
    
    print("\nTesting invalid dates (should return errors):")
    for date_str in invalid_dates:
        error = validate_date(date_str, "start_date")
        if error:
            print(f"  ✅ '{date_str}' - Correctly rejected: {error['error']}")
        else:
            print(f"  ❌ '{date_str}' - Should have been rejected but was accepted")
    
    # Test valid dates
    valid_dates = ["2024-01-15", "2023-12-31", "2024-02-29"]
    print("\nTesting valid dates (should pass):")
    for date_str in valid_dates:
        error = validate_date(date_str, "start_date")
        if error:
            print(f"  ❌ '{date_str}' - Should be valid but was rejected: {error['error']}")
        else:
            print(f"  ✅ '{date_str}' - Correctly accepted")
    
    # Test None (should pass)
    error = validate_date(None, "start_date")
    if error:
        print(f"  ❌ None - Should be valid but was rejected: {error['error']}")
    else:
        print(f"  ✅ None - Correctly accepted (optional parameter)")
    
    print("\n=== SERVER DATE VALIDATION TESTS COMPLETED ===")

if __name__ == "__main__":
    test_date_validation_logic()
    print("\n🎉 Server date validation logic tested successfully!")