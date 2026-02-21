"""Configuration helpers for environment-driven defaults."""

from __future__ import annotations

import os

DEFAULT_DATA_PATH = "data/data.xlsx"
DEFAULT_EXPORT_DIR = "exports"


def get_default_data_path() -> str:
    """Return workbook path from environment or fallback default."""
    return os.getenv("DHVIZ_DATA_PATH", DEFAULT_DATA_PATH)


def get_default_export_dir() -> str:
    """Return export directory from environment or fallback default."""
    return os.getenv("DHVIZ_EXPORT_DIR", DEFAULT_EXPORT_DIR)
