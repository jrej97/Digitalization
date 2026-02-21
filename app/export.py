"""Export helpers for CSV and GEXF graph artifacts."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from typing import Any

import pandas as pd

from app.provenance import WELL_KNOWN_METADATA_COLS
from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


def _ordered_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    """Return required columns first, then well-known metadata extras, then other extras."""
    required_present = [column for column in required_columns if column in df.columns]
    extra_columns = [column for column in df.columns if column not in required_columns]
    metadata_extras = [column for column in WELL_KNOWN_METADATA_COLS if column in extra_columns]
    other_extras = [column for column in extra_columns if column not in WELL_KNOWN_METADATA_COLS]
    return [*required_present, *metadata_extras, *other_extras]


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



def _filled_count(series: pd.Series) -> int:
    values = series.fillna('').astype(str).str.strip()
    return int(values.ne('').sum())


def _confidence_stats(df: pd.DataFrame) -> tuple[float, float, float] | None:
    if 'confidence' not in df.columns:
        return None
    confidence_values = pd.to_numeric(df['confidence'], errors='coerce').dropna()
    if confidence_values.empty:
        return None
    return float(confidence_values.min()), float(confidence_values.mean()), float(confidence_values.max())

def export_summary(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, out_path: str = "exports/EXPORT_SUMMARY.md") -> str:
    """Export a thesis-friendly markdown summary for the current dataset."""
    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    node_counts = nodes_df['type'].astype(str).value_counts().sort_index()
    edge_counts = edges_df['relationship_type'].astype(str).value_counts().sort_index()

    node_extras = [column for column in nodes_df.columns if column not in REQUIRED_NODE_COLS]
    edge_extras = [column for column in edges_df.columns if column not in REQUIRED_EDGE_COLS]

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        '# Export Summary',
        '',
        f'- Timestamp (UTC): {timestamp}',
        f'- Node count: {len(nodes_df)}',
        f'- Edge count: {len(edges_df)}',
        '',
        '## Nodes by type',
    ]

    if node_counts.empty:
        lines.append('- (none)')
    else:
        lines.extend(f'- {node_type}: {count}' for node_type, count in node_counts.items())

    lines.extend(['', '## Edges by relationship_type'])
    if edge_counts.empty:
        lines.append('- (none)')
    else:
        lines.extend(f'- {rel_type}: {count}' for rel_type, count in edge_counts.items())

    lines.extend(['', '## Provenance coverage'])
    if 'source_ref' in nodes_df.columns:
        node_source_count = _filled_count(nodes_df['source_ref'])
        lines.append(f'- Nodes with source_ref: {node_source_count}/{len(nodes_df)} ({(node_source_count / len(nodes_df) * 100) if len(nodes_df) else 0:.1f}%)')
    if 'source_ref' in edges_df.columns:
        edge_source_count = _filled_count(edges_df['source_ref'])
        lines.append(f'- Edges with source_ref: {edge_source_count}/{len(edges_df)} ({(edge_source_count / len(edges_df) * 100) if len(edges_df) else 0:.1f}%)')

    node_confidence = _confidence_stats(nodes_df)
    if node_confidence is not None:
        lines.append('- Node confidence (min/mean/max): ' + f'{node_confidence[0]:.3f}/{node_confidence[1]:.3f}/{node_confidence[2]:.3f}')
    edge_confidence = _confidence_stats(edges_df)
    if edge_confidence is not None:
        lines.append('- Edge confidence (min/mean/max): ' + f'{edge_confidence[0]:.3f}/{edge_confidence[1]:.3f}/{edge_confidence[2]:.3f}')

    if 'date' in nodes_df.columns:
        lines.append(f"- Nodes with date: {_filled_count(nodes_df['date'])}/{len(nodes_df)}")
    if 'date' in edges_df.columns:
        lines.append(f"- Edges with date: {_filled_count(edges_df['date'])}/{len(edges_df)}")
    if lines[-1] == '## Provenance coverage':
        lines.append('- (no provenance columns found)')

    lines.extend(['', '## Extra columns'])
    lines.append('- Nodes extras: ' + (', '.join(sorted(node_extras)) if node_extras else '(none)'))
    lines.append('- Edges extras: ' + (', '.join(sorted(edge_extras)) if edge_extras else '(none)'))
    lines.append('')

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    return str(output_path)
