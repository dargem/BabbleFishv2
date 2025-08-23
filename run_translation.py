#!/usr/bin/env python3
"""Entry point for BabbleFish Translation System."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main_refactored import run_translation

if __name__ == "__main__":
    run_translation()
