from pathlib import Path

import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.export import export_csv
from app.io_excel import load_workbook, save_workbook


def test_data_path_env_override_is_used(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    workbook_path = tmp_path / "custom_data.xlsx"
    monkeypatch.setenv("DHVIZ_DATA_PATH", str(workbook_path))

    nodes_df = pd.DataFrame(
        [{"id": "n1", "label": "Node", "type": "Person", "description": ""}]
    )
    edges_df = pd.DataFrame(
        [
            {
                "source": "n1",
                "target": "n1",
                "relationship_type": "self",
                "description": "",
            }
        ]
    )

    save_workbook(nodes_df, edges_df)
    loaded_nodes, loaded_edges = load_workbook()

    assert workbook_path.exists()
    assert len(loaded_nodes) == 1
    assert len(loaded_edges) == 1


def test_export_dir_env_override_is_used(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    export_dir = tmp_path / "custom_exports"
    monkeypatch.setenv("DHVIZ_EXPORT_DIR", str(export_dir))

    nodes_df = pd.DataFrame(
        [{"id": "n1", "label": "Node", "type": "Person", "description": ""}]
    )
    edges_df = pd.DataFrame(
        [
            {
                "source": "n1",
                "target": "n1",
                "relationship_type": "self",
                "description": "",
            }
        ]
    )

    nodes_path, edges_path = export_csv(nodes_df, edges_df)

    assert Path(nodes_path).parent == export_dir
    assert Path(edges_path).parent == export_dir
    assert Path(nodes_path).exists()
    assert Path(edges_path).exists()
