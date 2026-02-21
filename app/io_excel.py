"""Excel loading utilities for the crime network workbook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.schema import (
    REQUIRED_EDGE_COLS,
    REQUIRED_NODE_COLS,
    SHEET_EDGES,
    SHEET_NODES,
)


def load_workbook(path: str = "data/data.xlsx") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load nodes and edges sheets from the workbook and perform minimal schema checks."""
    workbook_path = Path(path)
    if not workbook_path.exists():
        raise FileNotFoundError(
            "Workbook not found at 'data/data.xlsx'. "
            "Create data/data.xlsx with 'nodes' and 'edges' sheets."
        )

    excel_file = pd.ExcelFile(workbook_path, engine="openpyxl")
    available_sheets = set(excel_file.sheet_names)
    required_sheets = {SHEET_NODES, SHEET_EDGES}
    missing_sheets = sorted(required_sheets - available_sheets)
    if missing_sheets:
        missing = ", ".join(missing_sheets)
        raise ValueError(f"Workbook is missing required sheet(s): {missing}.")

    nodes_df = pd.read_excel(
        workbook_path,
        sheet_name=SHEET_NODES,
        engine="openpyxl",
    )
    edges_df = pd.read_excel(
        workbook_path,
        sheet_name=SHEET_EDGES,
        engine="openpyxl",
    )

    missing_node_cols = [col for col in REQUIRED_NODE_COLS if col not in nodes_df.columns]
    missing_edge_cols = [col for col in REQUIRED_EDGE_COLS if col not in edges_df.columns]

    errors: list[str] = []
    if missing_node_cols:
        errors.append(f"{SHEET_NODES}: {', '.join(missing_node_cols)}")
    if missing_edge_cols:
        errors.append(f"{SHEET_EDGES}: {', '.join(missing_edge_cols)}")

    if errors:
        raise ValueError(f"Workbook is missing required column(s): {'; '.join(errors)}.")

    return nodes_df, edges_df
