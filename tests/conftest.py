"""Shared test configuration."""

import sys
from pathlib import Path

# Ensure project root is available on ``sys.path`` for nested tests.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
