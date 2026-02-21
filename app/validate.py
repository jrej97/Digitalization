"""Validation helpers for nodes and edges DataFrames."""

from __future__ import annotations

from numbers import Integral

import pandas as pd

from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


ValidationIssue = dict[str, str | int | None]


def _missing_columns(df: pd.DataFrame, required_cols: list[str]) -> list[str]:
    return [col for col in required_cols if col not in df.columns]


def validate_data(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> list[ValidationIssue]:
    """Validate nodes and edges DataFrames and return error dictionaries."""
    issues: list[ValidationIssue] = []

    missing_node_cols = _missing_columns(nodes_df, REQUIRED_NODE_COLS)
    for col in missing_node_cols:
        issues.append(
            {
                "severity": "error",
                "where": "nodes",
                "row": None,
                "message": f"Missing required column '{col}' in nodes sheet",
            }
        )

    missing_edge_cols = _missing_columns(edges_df, REQUIRED_EDGE_COLS)
    for col in missing_edge_cols:
        issues.append(
            {
                "severity": "error",
                "where": "edges",
                "row": None,
                "message": f"Missing required column '{col}' in edges sheet",
            }
        )

    if missing_node_cols:
        return issues

    node_ids = nodes_df["id"]

    missing_node_ids = node_ids.isna()
    for row_index in nodes_df.index[missing_node_ids]:
        issues.append(
            {
                "severity": "error",
                "where": "nodes",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Missing node id at row {row_index}",
            }
        )

    duplicate_mask = node_ids.duplicated(keep=False) & node_ids.notna()
    for row_index in nodes_df.index[duplicate_mask]:
        duplicate_id = nodes_df.at[row_index, "id"]
        issues.append(
            {
                "severity": "error",
                "where": "nodes",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Duplicate node id '{duplicate_id}' at row {row_index}",
            }
        )

    if missing_edge_cols:
        return issues

    known_node_ids = set(node_ids.dropna().tolist())

    source_missing_mask = edges_df["source"].isna()
    target_missing_mask = edges_df["target"].isna()

    for row_index in edges_df.index[source_missing_mask]:
        issues.append(
            {
                "severity": "error",
                "where": "edges",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Missing edge source at row {row_index}",
            }
        )

    for row_index in edges_df.index[target_missing_mask]:
        issues.append(
            {
                "severity": "error",
                "where": "edges",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Missing edge target at row {row_index}",
            }
        )

    valid_source_mask = ~source_missing_mask
    unknown_source_mask = valid_source_mask & ~edges_df["source"].isin(known_node_ids)
    for row_index in edges_df.index[unknown_source_mask]:
        source_value = edges_df.at[row_index, "source"]
        issues.append(
            {
                "severity": "error",
                "where": "edges",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Unknown edge source '{source_value}' at row {row_index}",
            }
        )

    valid_target_mask = ~target_missing_mask
    unknown_target_mask = valid_target_mask & ~edges_df["target"].isin(known_node_ids)
    for row_index in edges_df.index[unknown_target_mask]:
        target_value = edges_df.at[row_index, "target"]
        issues.append(
            {
                "severity": "error",
                "where": "edges",
                "row": int(row_index) if isinstance(row_index, Integral) else row_index,
                "message": f"Unknown edge target '{target_value}' at row {row_index}",
            }
        )

    return issues
