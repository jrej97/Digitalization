"""Excel loading utilities for the crime network workbook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import get_default_data_path
from app.schema import (
    REQUIRED_EDGE_COLS,
    REQUIRED_NODE_COLS,
    SHEET_EDGES,
    SHEET_NODES,
)


def load_workbook(path: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load nodes and edges sheets from the workbook and perform minimal schema checks."""
    if path is None:
        path = get_default_data_path()
    workbook_path = Path(path)
    if not workbook_path.exists():
        raise FileNotFoundError(
            f"Workbook not found at '{workbook_path}'. "
            "Create the file with 'nodes' and 'edges' sheets "
            "or set DHVIZ_DATA_PATH to the correct workbook location."
        )

    try:
        excel_file = pd.ExcelFile(workbook_path, engine="openpyxl")
    except Exception as error:
        raise ValueError(
            f"Unable to read workbook '{workbook_path}'. "
            "Ensure it is a valid .xlsx file and is not locked by another application."
        ) from error
    available_sheets = set(excel_file.sheet_names)
    required_sheets = {SHEET_NODES, SHEET_EDGES}
    missing_sheets = sorted(required_sheets - available_sheets)
    if missing_sheets:
        missing = ", ".join(missing_sheets)
        raise ValueError(
            f"Workbook is missing required sheet(s): {missing}. "
            "Add the missing sheets and try again."
        )

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
        raise ValueError(
            f"Workbook is missing required column(s): {'; '.join(errors)}. "
            "Add the missing columns and try again."
        )

    return nodes_df, edges_df


def _ordered_columns(df: pd.DataFrame, required_cols: list[str]) -> list[str]:
    required = [col for col in required_cols if col in df.columns]
    extras = [col for col in df.columns if col not in required_cols]
    return required + extras


def save_workbook(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, path: str | None = None) -> None:
    """Persist nodes and edges dataframes to an Excel workbook using safe-write semantics."""
    import os

    if path is None:
        path = get_default_data_path()
    workbook_path = Path(path)
    workbook_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_nodes = nodes_df.loc[:, _ordered_columns(nodes_df, REQUIRED_NODE_COLS)]
    ordered_edges = edges_df.loc[:, _ordered_columns(edges_df, REQUIRED_EDGE_COLS)]

    temp_path = workbook_path.parent / f".tmp_{workbook_path.name}"

    try:
        with pd.ExcelWriter(temp_path, engine="openpyxl") as writer:
            ordered_nodes.to_excel(writer, sheet_name=SHEET_NODES, index=False)
            ordered_edges.to_excel(writer, sheet_name=SHEET_EDGES, index=False)
        os.replace(temp_path, workbook_path)
    except PermissionError as error:
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(
            f"Failed to save workbook to '{workbook_path}'. "
            "Check file permissions and close the file if it is open in another program."
        ) from error
    except Exception as error:
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(
            f"Failed to save workbook to '{workbook_path}'. "
            "Verify the destination path exists and is writable."
        ) from error
