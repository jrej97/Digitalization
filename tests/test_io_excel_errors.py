from pathlib import Path

import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.io_excel import load_workbook


def test_load_workbook_missing_file_has_actionable_message(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError) as error_info:
        load_workbook(str(missing_path))

    message = str(error_info.value)
    assert "Workbook not found" in message
    assert "DHVIZ_DATA_PATH" in message


def test_load_workbook_missing_required_columns_has_actionable_message(tmp_path: Path) -> None:
    workbook_path = tmp_path / "bad_columns.xlsx"
    nodes_df = pd.DataFrame({"id": ["n1"]})
    edges_df = pd.DataFrame({"source": ["n1"], "target": ["n2"]})

    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        nodes_df.to_excel(writer, sheet_name="nodes", index=False)
        edges_df.to_excel(writer, sheet_name="edges", index=False)

    with pytest.raises(ValueError) as error_info:
        load_workbook(str(workbook_path))

    message = str(error_info.value)
    assert "Workbook is missing required column(s)" in message
    assert "Add the missing columns and try again." in message
