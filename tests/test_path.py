#!/usr/bin/env python3
"""Test path conversion directly."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rgrep_mcp.ripgrep import RipgrepWrapper

def test_path_conversion():
    test_vault = Path(__file__).parent / "test_vault"
    print(f"Original path: {test_vault}")
    
    rg = RipgrepWrapper(str(test_vault))
    converted = rg._convert_path_for_rg(str(test_vault))
    print(f"Converted path: {converted}")
    
    # Test if we can build a command
    cmd = rg._build_rg_command("meeting")
    print(f"Command: {' '.join(cmd)}")

if __name__ == "__main__":
    test_path_conversion()