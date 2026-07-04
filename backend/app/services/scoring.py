"""Security score computation from a list of findings.

Scoring model (see docs/rules-engine.md):
    - start at 100 points
    - subtract a fixed weight per finding, based on its severity
    - clamp the result to [0, 100]
    - map the final score to a human-readable classification band
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel

from app.domain.findings import Finding
from app.domain.severity import SEVERITY_WEIGHTS, Severity

STARTING_SCORE = 100.0
MIN_SCORE = 0.0
MAX_SCORE = 100.0

_CLASSIFICATION_BANDS: tuple[tuple[float, str], ...] = (
    (90.0, "Excellent"),
    (75.0, "Good"),
    (50.0, "Needs improvement"),
    (25.0, "Risky"),
    (0.0, "Critical"),
)


class ScoreResult(BaseModel):
    score: float
    classification: str
    findings_by_severity: dict[Severity, int]

    @property
    def total_findings(self) -> int:
        return sum(self.findings_by_severity.values())


def classify(score: float) -> str:
    for threshold, label in _CLASSIFICATION_BANDS:
        if score >= threshold:
            return label
    return "Critical"


def compute_score(findings: list[Finding]) -> ScoreResult:
    counts = Counter(finding.severity for finding in findings)
    penalty = sum(SEVERITY_WEIGHTS[severity] * count for severity, count in counts.items())
    score = max(MIN_SCORE, min(MAX_SCORE, STARTING_SCORE - penalty))

    breakdown = {severity: counts.get(severity, 0) for severity in Severity}
    return ScoreResult(
        score=round(score, 2),
        classification=classify(score),
        findings_by_severity=breakdown,
    )
