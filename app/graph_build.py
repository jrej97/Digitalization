"""Build Cytoscape elements from validated node and edge tables."""

from __future__ import annotations

from typing import Any

import networkx as nx
import pandas as pd

from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


def _normalize_optional_text(value: Any) -> str:
    """Return an empty string for missing text values."""
    if value is None or pd.isna(value):
        return ""
    return str(value)


def _serialize_extra_value(value: Any) -> str | int | float | bool | None:
    """Serialize extra-column values into JSON-friendly primitive values."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (str, int, float)):
        if isinstance(value, float) and pd.isna(value):
            return ""
        return value
    return str(value)


def build_cytoscape_elements(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> list[dict[str, dict[str, Any]]]:
    """Convert nodes and edges tables into Cytoscape element dictionaries."""
    elements: list[dict[str, dict[str, Any]]] = []

    node_required = set(REQUIRED_NODE_COLS)
    edge_required = set(REQUIRED_EDGE_COLS)

    for _, row in nodes_df.iterrows():
        node_data: dict[str, Any] = {
            REQUIRED_NODE_COLS[0]: row[REQUIRED_NODE_COLS[0]],
            REQUIRED_NODE_COLS[1]: row[REQUIRED_NODE_COLS[1]],
            REQUIRED_NODE_COLS[2]: row[REQUIRED_NODE_COLS[2]],
            REQUIRED_NODE_COLS[3]: _normalize_optional_text(row[REQUIRED_NODE_COLS[3]]),
        }

        for column in nodes_df.columns:
            if column in node_required:
                continue
            node_data[column] = _serialize_extra_value(row[column])

        elements.append({"data": node_data})

    for row_index, row in edges_df.iterrows():
        source = row[REQUIRED_EDGE_COLS[0]]
        target = row[REQUIRED_EDGE_COLS[1]]
        relationship_type = row[REQUIRED_EDGE_COLS[2]]
        edge_id = f"{source}__{target}__{relationship_type}__{row_index}"

        edge_data: dict[str, Any] = {
            "id": edge_id,
            REQUIRED_EDGE_COLS[0]: source,
            REQUIRED_EDGE_COLS[1]: target,
            REQUIRED_EDGE_COLS[2]: relationship_type,
            REQUIRED_EDGE_COLS[3]: _normalize_optional_text(row[REQUIRED_EDGE_COLS[3]]),
        }

        for column in edges_df.columns:
            if column in edge_required:
                continue
            edge_data[column] = _serialize_extra_value(row[column])

        elements.append({"data": edge_data})

    return elements


def build_networkx_graph(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> nx.MultiGraph:
    """Build an undirected MultiGraph so duplicate source/target edges are preserved as parallel edges."""
    graph = nx.MultiGraph()

    node_required = set(REQUIRED_NODE_COLS)
    edge_required = set(REQUIRED_EDGE_COLS)

    for _, row in nodes_df.iterrows():
        node_id = row[REQUIRED_NODE_COLS[0]]
        node_attributes: dict[str, Any] = {
            REQUIRED_NODE_COLS[1]: row[REQUIRED_NODE_COLS[1]],
            REQUIRED_NODE_COLS[2]: row[REQUIRED_NODE_COLS[2]],
            REQUIRED_NODE_COLS[3]: _normalize_optional_text(row[REQUIRED_NODE_COLS[3]]),
        }

        for column in nodes_df.columns:
            if column in node_required:
                continue
            node_attributes[column] = _serialize_extra_value(row[column])

        graph.add_node(node_id, **node_attributes)

    for _, row in edges_df.iterrows():
        source = row[REQUIRED_EDGE_COLS[0]]
        target = row[REQUIRED_EDGE_COLS[1]]
        edge_attributes: dict[str, Any] = {
            REQUIRED_EDGE_COLS[2]: row[REQUIRED_EDGE_COLS[2]],
            REQUIRED_EDGE_COLS[3]: _normalize_optional_text(row[REQUIRED_EDGE_COLS[3]]),
        }

        for column in edges_df.columns:
            if column in edge_required:
                continue
            edge_attributes[column] = _serialize_extra_value(row[column])

        graph.add_edge(source, target, **edge_attributes)

    return graph
