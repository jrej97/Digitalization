from pathlib import Path

import pandas as pd

from app.io_excel import save_workbook
from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS, SHEET_EDGES, SHEET_NODES


def test_save_workbook_writes_both_sheets_and_preserves_extra_columns(tmp_path: Path) -> None:
    nodes_df = pd.DataFrame(
        [
            {
                "id": "n1",
                "label": "Alice",
                "type": "person",
                "description": "desc",
                "risk_score": 8,
            },
            {
                "id": "n2",
                "label": "Bob",
                "type": "person",
                "description": "desc2",
                "risk_score": 3,
            },
        ]
    )
    edges_df = pd.DataFrame(
        [
            {
                "source": "n1",
                "target": "n2",
                "relationship_type": "knows",
                "description": "sample",
                "weight": 0.7,
            }
        ]
    )

    workbook_path = tmp_path / "data.xlsx"
    save_workbook(nodes_df, edges_df, path=str(workbook_path))

    workbook = pd.ExcelFile(workbook_path, engine="openpyxl")
    assert SHEET_NODES in workbook.sheet_names
    assert SHEET_EDGES in workbook.sheet_names

    saved_nodes = pd.read_excel(workbook_path, sheet_name=SHEET_NODES, engine="openpyxl")
    saved_edges = pd.read_excel(workbook_path, sheet_name=SHEET_EDGES, engine="openpyxl")

    for required_col in REQUIRED_NODE_COLS:
        assert required_col in saved_nodes.columns
    for required_col in REQUIRED_EDGE_COLS:
        assert required_col in saved_edges.columns

    assert "risk_score" in saved_nodes.columns
    assert "weight" in saved_edges.columns

    assert list(saved_nodes.columns[: len(REQUIRED_NODE_COLS)]) == REQUIRED_NODE_COLS
    assert list(saved_edges.columns[: len(REQUIRED_EDGE_COLS)]) == REQUIRED_EDGE_COLS

    assert len(saved_nodes) == len(nodes_df)
    assert len(saved_edges) == len(edges_df)
