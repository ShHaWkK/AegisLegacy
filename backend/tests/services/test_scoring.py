from __future__ import annotations

import pytest

from app.domain.findings import Finding
from app.domain.severity import Severity
from app.services.scoring import classify, compute_score


def _finding(severity: Severity, rule_id: str = "R-1") -> Finding:
    return Finding(
        rule_id=rule_id,
        title="t",
        severity=severity,
        category="c",
        language="python",
        file_path="f.py",
        line_number=1,
        matched_text="m",
        description="d",
        recommendation="r",
    )


def test_no_findings_gives_perfect_score() -> None:
    result = compute_score([])

    assert result.score == 100.0
    assert result.classification == "Excellent"
    assert result.total_findings == 0


def test_single_critical_finding_subtracts_twenty_points() -> None:
    result = compute_score([_finding(Severity.CRITICAL)])

    assert result.score == 80.0
    assert result.classification == "Good"


@pytest.mark.parametrize(
    "severity,expected_penalty",
    [
        (Severity.CRITICAL, 20.0),
        (Severity.HIGH, 10.0),
        (Severity.MEDIUM, 5.0),
        (Severity.LOW, 2.0),
        (Severity.INFO, 0.5),
    ],
)
def test_each_severity_has_the_documented_weight(
    severity: Severity, expected_penalty: float
) -> None:
    result = compute_score([_finding(severity)])

    assert result.score == pytest.approx(100.0 - expected_penalty)


def test_score_is_clamped_to_zero_and_never_negative() -> None:
    findings = [_finding(Severity.CRITICAL, rule_id=f"R-{i}") for i in range(10)]

    result = compute_score(findings)

    assert result.score == 0.0
    assert result.classification == "Critical"


def test_findings_by_severity_breakdown_counts_correctly() -> None:
    findings = [
        _finding(Severity.CRITICAL, "R-1"),
        _finding(Severity.CRITICAL, "R-2"),
        _finding(Severity.LOW, "R-3"),
    ]

    result = compute_score(findings)

    assert result.findings_by_severity[Severity.CRITICAL] == 2
    assert result.findings_by_severity[Severity.LOW] == 1
    assert result.findings_by_severity[Severity.HIGH] == 0
    assert result.total_findings == 3


@pytest.mark.parametrize(
    "score,expected",
    [
        (100.0, "Excellent"),
        (90.0, "Excellent"),
        (89.9, "Good"),
        (75.0, "Good"),
        (74.9, "Needs improvement"),
        (50.0, "Needs improvement"),
        (49.9, "Risky"),
        (25.0, "Risky"),
        (24.9, "Critical"),
        (0.0, "Critical"),
    ],
)
def test_classification_bands_match_boundaries(score: float, expected: str) -> None:
    assert classify(score) == expected
