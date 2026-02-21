"""Helpers for optional provenance metadata fields."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd


WELL_KNOWN_METADATA_COLS = ["source_ref", "date", "confidence"]
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_valid_optional_date(value: str) -> bool:
    """Return True when date is empty or follows YYYY-MM-DD."""
    if value == "":
        return True
    return bool(_DATE_PATTERN.match(value))


def parse_optional_confidence(value: Any) -> tuple[bool, float | str]:
    """Parse confidence values as empty or float in range [0, 1]."""
    if value is None:
        return True, ""
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return True, ""
        value = stripped
    if isinstance(value, float) and pd.isna(value):
        return True, ""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return False, ""
    if parsed < 0 or parsed > 1:
        return False, ""
    return True, parsed


def ensure_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the known metadata columns exist on a dataframe."""
    updated = df.copy()
    for column in WELL_KNOWN_METADATA_COLS:
        if column not in updated.columns:
            updated[column] = ""
    return updated

