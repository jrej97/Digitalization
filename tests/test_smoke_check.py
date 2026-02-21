from pathlib import Path

from scripts.smoke_check import run_smoke_check


def test_run_smoke_check_generates_expected_artifacts(tmp_path: Path) -> None:
    paths = run_smoke_check(base_dir=tmp_path)

    expected_keys = {"workbook", "nodes_csv", "edges_csv", "graph_gexf", "summary_md"}
    assert set(paths.keys()) == expected_keys

    for artifact_path in paths.values():
        assert artifact_path.exists()

    assert paths["workbook"].name == "data.xlsx"
    assert paths["nodes_csv"].name == "nodes.csv"
    assert paths["edges_csv"].name == "edges.csv"
    assert paths["graph_gexf"].name == "graph.gexf"
    assert paths["summary_md"].name == "EXPORT_SUMMARY.md"
