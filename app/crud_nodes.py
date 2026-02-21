"""Node CRUD helpers for in-memory DataFrame operations."""

from __future__ import annotations

import pandas as pd


NODE_TYPE_OPTIONS = ['Person', 'Place', 'Institution', 'Group']


def is_unique_node_id(nodes_df: pd.DataFrame, node_id: str, *, exclude_index: int | None = None) -> bool:
    """Return whether node_id is unique in nodes_df, excluding one row index when editing."""
    filtered = nodes_df
    if exclude_index is not None:
        filtered = filtered.drop(index=exclude_index, errors='ignore')
    return not filtered['id'].astype(str).eq(node_id).any()


def edge_reference_count(edges_df: pd.DataFrame, node_id: str) -> int:
    """Count edges that reference node_id as source or target."""
    source_matches = edges_df['source'].astype(str).eq(node_id)
    target_matches = edges_df['target'].astype(str).eq(node_id)
    return int((source_matches | target_matches).sum())


def can_delete_node(edges_df: pd.DataFrame, node_id: str) -> tuple[bool, int]:
    """Return (allowed, reference_count) for deleting the given node."""
    count = edge_reference_count(edges_df, node_id)
    return count == 0, count
