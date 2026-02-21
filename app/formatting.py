"""Formatting helpers for read-only inspector content."""

from __future__ import annotations

from typing import Any

_MAX_VALUE_LENGTH = 200


def _display_value(value: Any) -> str:
    """Normalize missing values and truncate large values for inspector display."""
    if value is None:
        return ''
    text = str(value)
    if len(text) > _MAX_VALUE_LENGTH:
        return f'{text[:_MAX_VALUE_LENGTH]}...'
    return text


def format_inspector_rows(kind: str, data: dict[str, Any]) -> list[tuple[str, str]]:
    """Return ordered key/value rows to render for the selected node or edge."""
    safe_data = data if isinstance(data, dict) else {}

    if kind == 'node':
        core_keys = ['id', 'label', 'type', 'description']
    elif kind == 'edge':
        core_keys = ['id', 'source', 'target', 'relationship_type', 'description']
    else:
        return []

    rows = [(key, _display_value(safe_data.get(key, ''))) for key in core_keys]

    extra_keys = sorted(key for key in safe_data.keys() if key not in core_keys)
    for key in extra_keys:
        rows.append((key, _display_value(safe_data.get(key, ''))))

    return rows
