"""Severity levels and their scoring weights.

Weights follow the AegisLegacy scoring model documented in
docs/rules-engine.md: each finding of a given severity subtracts a fixed
number of points from a starting score of 100.
"""

from __future__ import annotations

from enum import StrEnum


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


SEVERITY_WEIGHTS: dict[Severity, float] = {
    Severity.CRITICAL: 20.0,
    Severity.HIGH: 10.0,
    Severity.MEDIUM: 5.0,
    Severity.LOW: 2.0,
    Severity.INFO: 0.5,
}

# Order used for sorting findings from most to least severe
SEVERITY_ORDER: tuple[Severity, ...] = (
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
)


def severity_rank(severity: Severity) -> int:
    """Lower rank means more severe. Useful as a sort key."""
    return SEVERITY_ORDER.index(severity)
