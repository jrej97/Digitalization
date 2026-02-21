from pathlib import Path

import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.export import export_csv, export_summary
from app.io_excel import load_workbook
from app.sample_data import create_sample_workbook


def test_sample_workbook_generation_is_deterministic(tmp_path: Path) -> None:
    workbook_one = tmp_path / "sample_one.xlsx"
    workbook_two = tmp_path / "sample_two.xlsx"

    create_sample_workbook(str(workbook_one))
    create_sample_workbook(str(workbook_two))

    nodes_one, edges_one = load_workbook(str(workbook_one))
    nodes_two, edges_two = load_workbook(str(workbook_two))

    assert nodes_one.columns.tolist() == nodes_two.columns.tolist()
    assert edges_one.columns.tolist() == edges_two.columns.tolist()

    pd.testing.assert_frame_equal(nodes_one, nodes_two, check_like=False)
    pd.testing.assert_frame_equal(edges_one, edges_two, check_like=False)


def test_export_csv_is_deterministic_across_runs(tmp_path: Path) -> None:
    nodes_df = pd.DataFrame(
        {
            "id": ["N2", "N1"],
            "label": ["B", "A"],
            "type": ["org", "person"],
            "description": ["", ""],
            "z_extra": [2, 1],
            "a_extra": ["x", "y"],
        }
    )
    edges_df = pd.DataFrame(
        {
            "source": ["N2", "N1", "N1"],
            "target": ["N1", "N2", "N2"],
            "relationship_type": ["LINKED", "linked", "linked"],
            "description": ["", "", ""],
            "z_edge": [3, 1, 2],
        }
    )

    out_one = tmp_path / "run_one"
    out_two = tmp_path / "run_two"

    nodes_one, edges_one = export_csv(nodes_df, edges_df, out_dir=str(out_one))
    nodes_two, edges_two = export_csv(nodes_df, edges_df, out_dir=str(out_two))

    assert Path(nodes_one).read_bytes() == Path(nodes_two).read_bytes()
    assert Path(edges_one).read_bytes() == Path(edges_two).read_bytes()


def test_export_summary_is_deterministic_across_runs(tmp_path: Path) -> None:
    nodes_df = pd.DataFrame(
        {
            "id": ["N2", "N1"],
            "label": ["Node 2", "Node 1"],
            "type": ["Place", "Person"],
            "description": ["", ""],
            "source_ref": ["Doc B", "Doc A"],
            "custom": [1, 2],
        }
    )
    edges_df = pd.DataFrame(
        {
            "source": ["N2", "N1"],
            "target": ["N1", "N2"],
            "relationship_type": ["VISITED", "AFFILIATED_WITH"],
            "description": ["", ""],
            "source_ref": ["Ref 2", "Ref 1"],
            "weight": [0.2, 0.8],
        }
    )

    out_one = tmp_path / "summary_one.md"
    out_two = tmp_path / "summary_two.md"

    export_summary(nodes_df, edges_df, out_path=str(out_one))
    export_summary(nodes_df, edges_df, out_path=str(out_two))

    assert out_one.read_text(encoding="utf-8") == out_two.read_text(encoding="utf-8")
