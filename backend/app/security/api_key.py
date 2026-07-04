"""API key verification, isolated so it can be audited and tested alone.

Uses a constant-time comparison to avoid leaking the expected key's length
or content through response-timing side channels.
"""

from __future__ import annotations

import hmac


def verify_api_key(provided: str | None, expected: str) -> bool:
    if not provided:
        return False
    return hmac.compare_digest(provided, expected)
