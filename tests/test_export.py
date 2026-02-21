from pathlib import Path

import pytest

pytest.importorskip("pandas")
import pandas as pd


from app.export import export_csv, export_gexf
from app.graph_build import build_networkx_graph
from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


def test_export_csv_writes_expected_files_and_columns(tmp_path: Path) -> None:
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2'],
            'label': ['Node 1', 'Node 2'],
            'type': ['person', 'org'],
            'description': ['', 'Known associate'],
            'source_ref': ['Doc A', 'Doc B'],
            'date': ['2024-01-01', ''],
            'confidence': [0.8, ''],
            'risk_score': [3, 7],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1'],
            'target': ['N2'],
            'relationship_type': ['linked'],
            'description': ['Seen together'],
            'source_ref': ['Doc A'],
            'date': ['2024-01-01'],
            'confidence': [0.9],
            'strength': [0.8],
        }
    )

    out_dir = tmp_path / 'exports'
    nodes_path, edges_path = export_csv(nodes_df, edges_df, out_dir=str(out_dir))

    nodes_export = Path(nodes_path)
    edges_export = Path(edges_path)

    assert nodes_export.exists()
    assert edges_export.exists()

    exported_nodes_df = pd.read_csv(nodes_export)
    exported_edges_df = pd.read_csv(edges_export)

    assert exported_nodes_df.columns[: len(REQUIRED_NODE_COLS)].tolist() == REQUIRED_NODE_COLS
    assert exported_edges_df.columns[: len(REQUIRED_EDGE_COLS)].tolist() == REQUIRED_EDGE_COLS

    expected_node_order = [*REQUIRED_NODE_COLS, 'source_ref', 'date', 'confidence', 'risk_score']
    expected_edge_order = [*REQUIRED_EDGE_COLS, 'source_ref', 'date', 'confidence', 'strength']
    assert exported_nodes_df.columns.tolist() == expected_node_order
    assert exported_edges_df.columns.tolist() == expected_edge_order

    assert len(exported_nodes_df) == len(nodes_df)
    assert len(exported_edges_df) == len(edges_df)


def test_export_gexf_writes_nonempty_file(tmp_path: Path) -> None:
    pytest.importorskip("networkx")
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2'],
            'label': ['Node 1', 'Node 2'],
            'type': ['person', 'org'],
            'description': ['', ''],
            'source_ref': ['Doc A', 'Doc B'],
            'date': ['2024-01-01', '2024-01-02'],
            'confidence': [0.7, 0.9],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1'],
            'target': ['N2'],
            'relationship_type': ['linked'],
            'description': [''],
            'source_ref': ['Doc A'],
            'date': ['2024-01-01'],
            'confidence': [0.85],
        }
    )

    graph = build_networkx_graph(nodes_df, edges_df)
    gexf_path = tmp_path / 'exports' / 'graph.gexf'

    exported_path = Path(export_gexf(graph, out_path=str(gexf_path)))

    assert exported_path.exists()
    assert exported_path.stat().st_size > 0

    content = exported_path.read_text(encoding='utf-8')
    assert 'relationship_type' in content
    assert 'source_ref' in content
    assert 'confidence' in content
