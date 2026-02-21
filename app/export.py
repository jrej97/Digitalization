"""Export helpers for CSV and GEXF graph artifacts."""

from __future__ import annotations

from pathlib import Path

from typing import Any

import pandas as pd

from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


def _ordered_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    """Return required columns first, then any extras in their existing order."""
    extra_columns = [column for column in df.columns if column not in required_columns]
    return [*required_columns, *extra_columns]


def export_csv(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, out_dir: str = "exports") -> tuple[str, str]:
    """Export nodes/edges dataframes to UTF-8 CSV files in the given output directory."""
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = output_dir / "nodes.csv"
    edges_path = output_dir / "edges.csv"

    ordered_nodes = nodes_df.loc[:, _ordered_columns(nodes_df, REQUIRED_NODE_COLS)]
    ordered_edges = edges_df.loc[:, _ordered_columns(edges_df, REQUIRED_EDGE_COLS)]

    ordered_nodes.to_csv(nodes_path, index=False, encoding="utf-8")
    ordered_edges.to_csv(edges_path, index=False, encoding="utf-8")

    return str(nodes_path), str(edges_path)


def export_gexf(nx_graph: Any, out_path: str = "exports/graph.gexf") -> str:
    """Export a NetworkX graph as GEXF at the requested output path."""
    import networkx as nx

    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gexf(nx_graph, output_path)
    return str(output_path)
