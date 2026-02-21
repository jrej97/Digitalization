"""Helpers for tracking unsaved in-memory changes."""

from __future__ import annotations

_dirty = False


def mark_dirty() -> None:
    """Mark current workbook state as having unsaved changes."""
    global _dirty
    _dirty = True


def mark_clean() -> None:
    """Mark current workbook state as persisted."""
    global _dirty
    _dirty = False


def is_dirty() -> bool:
    """Return whether there are unsaved in-memory changes."""
    return _dirty
