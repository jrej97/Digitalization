"""Graph filtering helpers for Graph view controls."""

from __future__ import annotations

import pandas as pd


DEFAULT_NODE_TYPE_FILTER = 'All'
DEFAULT_RELATIONSHIP_FILTER = 'All'
DEFAULT_SEARCH_FILTER = ''


def default_filters() -> tuple[str, str, str]:
    """Return default Graph view filter values."""
    return DEFAULT_NODE_TYPE_FILTER, DEFAULT_RELATIONSHIP_FILTER, DEFAULT_SEARCH_FILTER


def apply_filters(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    type_filter: str,
    rel_filter: str,
    search: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return filtered nodes and edges based on type, relationship type, and node-label search."""
    filtered_nodes = nodes_df.copy()

    normalized_type = (type_filter or DEFAULT_NODE_TYPE_FILTER).strip()
    if normalized_type and normalized_type != DEFAULT_NODE_TYPE_FILTER:
        filtered_nodes = filtered_nodes[filtered_nodes['type'].astype(str) == normalized_type]

    normalized_search = (search or '').strip().lower()
    if normalized_search:
        filtered_nodes = filtered_nodes[
            filtered_nodes['label'].astype(str).str.lower().str.contains(normalized_search, na=False)
        ]

    remaining_ids = set(filtered_nodes['id'].astype(str))
    filtered_edges = edges_df.copy()
    filtered_edges = filtered_edges[
        filtered_edges['source'].astype(str).isin(remaining_ids) & filtered_edges['target'].astype(str).isin(remaining_ids)
    ]

    normalized_rel = (rel_filter or DEFAULT_RELATIONSHIP_FILTER).strip()
    if normalized_rel and normalized_rel != DEFAULT_RELATIONSHIP_FILTER:
        filtered_edges = filtered_edges[filtered_edges['relationship_type'].astype(str) == normalized_rel]

    return filtered_nodes.reset_index(drop=True), filtered_edges.reset_index(drop=True)
