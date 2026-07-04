"""Normalized findings produced by the rules engine."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.severity import Severity


class Finding(BaseModel):
    """A single rule match against a specific location in a scanned file."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    title: str
    severity: Severity
    category: str
    language: str
    file_path: str = Field(description="Path relative to the scan root")
    line_number: int = Field(ge=1)
    matched_text: str
    description: str
    recommendation: str

    def as_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")
