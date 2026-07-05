"""Pydantic schemas for the HTTP surface — the wire format.

Kept separate from both the domain models (app/domain) and the storage
models (app/repositories/models.py) so each can evolve independently: a
database column rename shouldn't have to be an API breaking change, and
vice versa.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ScanCreate(BaseModel):
    target_path: str = Field(
        min_length=1, description="Path to scan on the server's filesystem."
    )


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_path: str
    status: str
    score: float
    classification: str
    findings_count: int
    created_at: datetime


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: str
    title: str
    severity: str
    category: str
    language: str
    file_path: str
    line_number: int
    matched_text: str
    description: str
    recommendation: str


class ScoreRead(BaseModel):
    score: float
    classification: str
    findings_count: int


class RuleRead(BaseModel):
    id: str
    language: str
    severity: str
    title: str
    category: str
    description: str
    recommendation: str
    patterns: list[str]


class Page(BaseModel, Generic[T]):  # noqa: UP046 - pydantic v2 exige Generic[T], pas la syntaxe PEP 695
    items: list[T]
    total: int
    page: int
    page_size: int
