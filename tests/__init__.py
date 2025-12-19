"""
Unit Tests Configuration

Base configuration for unit tests.
"""

import sys
from pathlib import Path

import pytest

# Adds the root directory to the path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))
