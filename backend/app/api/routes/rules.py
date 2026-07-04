from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import RuleRead
from app.core.config import Settings, get_settings
from app.rules.loader import RuleLoadError, load_rules_from_directory

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("", response_model=list[RuleRead])
def list_rules(settings: Settings = Depends(get_settings)) -> list[RuleRead]:
    try:
        rules = load_rules_from_directory(settings.rules_dir)
    except RuleLoadError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rules configuration error: {exc}",
        ) from exc

    return [
        RuleRead(
            id=rule.id,
            language=rule.language.value,
            severity=rule.severity.value,
            title=rule.title,
            category=rule.category,
            description=rule.description,
            recommendation=rule.recommendation,
            patterns=rule.patterns,
        )
        for rule in rules
    ]
