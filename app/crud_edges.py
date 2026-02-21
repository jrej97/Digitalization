"""Edge CRUD helpers for in-memory DataFrame operations."""

from __future__ import annotations

import pandas as pd


def can_add_or_edit_edge(
    nodes_df: pd.DataFrame,
    source: str,
    target: str,
    relationship_type: str,
) -> tuple[bool, str]:
    """Validate edge dialog inputs against node ids and basic relationship constraints."""
    if not source:
        return False, 'source is required'
    if not target:
        return False, 'target is required'
    if not relationship_type:
        return False, 'relationship_type is required'

    node_ids = set(nodes_df['id'].astype(str).tolist())
    if source not in node_ids:
        return False, f"source '{source}' does not exist"
    if target not in node_ids:
        return False, f"target '{target}' does not exist"
    if source == target:
        return False, 'source and target must be different (self-loops are not allowed yet)'

    return True, ''
