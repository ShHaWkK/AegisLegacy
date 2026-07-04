"""Shared pytest configuration.

Ensures `app` is importable when tests are run directly (without an
editable install), by putting the backend/ directory on sys.path.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
