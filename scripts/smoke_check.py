"""Run a no-UI smoke check for workbook generation, validation, and exports."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.export import export_csv, export_gexf, export_summary
from app.graph_build import build_networkx_graph
from app.io_excel import load_workbook
from app.sample_data import create_sample_workbook
from app.validate import validate_data


def run_smoke_check(base_dir: Path | None = None) -> dict[str, Path]:
    """Create sample workbook, validate data, and export artifacts into temporary paths."""
    if base_dir is None:
        root_dir = Path(tempfile.mkdtemp(prefix="digitalization_smoke_"))
    else:
        root_dir = Path(base_dir)

    root_dir.mkdir(parents=True, exist_ok=True)

    workbook_path = root_dir / "data" / "data.xlsx"
    exports_dir = root_dir / "exports"

    create_sample_workbook(str(workbook_path))
    nodes_df, edges_df = load_workbook(str(workbook_path))

    issues = validate_data(nodes_df, edges_df)
    if issues:
        raise RuntimeError(f"Smoke check failed validation: {issues}")

    nodes_csv, edges_csv = export_csv(nodes_df, edges_df, out_dir=str(exports_dir))

    graph = build_networkx_graph(nodes_df, edges_df)
    gexf_path = export_gexf(graph, out_path=str(exports_dir / "graph.gexf"))
    summary_path = export_summary(nodes_df, edges_df, out_path=str(exports_dir / "EXPORT_SUMMARY.md"))

    paths = {
        "workbook": workbook_path,
        "nodes_csv": Path(nodes_csv),
        "edges_csv": Path(edges_csv),
        "graph_gexf": Path(gexf_path),
        "summary_md": Path(summary_path),
    }

    for path in paths.values():
        if not path.exists():
            raise RuntimeError(f"Smoke check expected artifact missing: {path}")

    return paths


def main() -> None:
    """CLI entry point for smoke check."""
    paths = run_smoke_check()
    print("Smoke check artifacts:")
    for name, path in paths.items():
        print(f"- {name}: {path}")
    print("OK")


if __name__ == "__main__":
    main()
