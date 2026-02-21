from pathlib import Path

import pytest

pytest.importorskip("pandas")

from app.io_excel import load_workbook
from app.sample_data import create_sample_workbook
from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS
from app.validate import validate_data


def test_create_sample_workbook_generates_valid_data(tmp_path: Path) -> None:
    workbook_path = tmp_path / "sample" / "data.xlsx"

    created_path = create_sample_workbook(str(workbook_path))

    assert Path(created_path).exists()

    nodes_df, edges_df = load_workbook(str(workbook_path))

    for col in REQUIRED_NODE_COLS:
        assert col in nodes_df.columns
    for col in REQUIRED_EDGE_COLS:
        assert col in edges_df.columns

    assert len(nodes_df) > 0
    assert len(edges_df) > 0

    assert validate_data(nodes_df, edges_df) == []
