"""Utilities for generating a starter workbook with sample graph data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import get_default_data_path
from app.io_excel import save_workbook
from app.schema import REQUIRED_EDGE_COLS, REQUIRED_NODE_COLS


def _ordered_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    """Return required columns first, then deterministically sorted extra columns."""
    required = [column for column in required_columns if column in df.columns]
    extras = sorted(column for column in df.columns if column not in required_columns)
    return [*required, *extras]


def _sort_sample_edges(df: pd.DataFrame) -> pd.DataFrame:
    """Return edges sorted in a deterministic order while preserving ties."""
    ranked = df.assign(
        relationship_type=df["relationship_type"].astype(str).str.strip().str.lower(),
        _original_order=range(len(df)),
    )
    sorted_df = ranked.sort_values(
        by=["source", "target", "relationship_type", "_original_order"],
        kind="mergesort",
    )
    return sorted_df.drop(columns=["_original_order"]).reset_index(drop=True)


def create_sample_workbook(path: str | None = None) -> str:
    """Create a starter workbook at path and return the created file path."""
    if path is None:
        path = get_default_data_path()
    workbook_path = Path(path)
    workbook_path.parent.mkdir(parents=True, exist_ok=True)

    nodes_df = pd.DataFrame(
        [
            {
                "id": "p_alice",
                "label": "Alice Romano",
                "type": "Person",
                "description": "Financial coordinator with links to multiple entities",
                "notes": "Primary analyst interview source",
            },
            {
                "id": "p_bruno",
                "label": "Bruno Keller",
                "type": "Person",
                "description": "Operations contact observed in site visits",
                "notes": "Seen in 2022 transfer records",
            },
            {
                "id": "p_clara",
                "label": "Clara Mendes",
                "type": "Person",
                "description": "Board advisor and institutional liaison",
                "notes": "Maintains communication logs",
            },
            {
                "id": "pl_harbor",
                "label": "Harbor District",
                "type": "Place",
                "description": "Logistics zone used for meetings",
                "notes": "Geo tag HD-14",
            },
            {
                "id": "pl_university",
                "label": "North University",
                "type": "Place",
                "description": "Campus where recruitment events occurred",
                "notes": "Public venue",
            },
            {
                "id": "i_meridian",
                "label": "Meridian Labs",
                "type": "Institution",
                "description": "Private contractor in procurement chain",
                "notes": "Registered in 2017",
            },
            {
                "id": "i_cityhall",
                "label": "City Hall",
                "type": "Institution",
                "description": "Municipal authority issuing permits",
                "notes": "Open data records available",
            },
            {
                "id": "g_tide",
                "label": "Tide Circle",
                "type": "Group",
                "description": "Coordination group connecting field actors",
                "notes": "Weekly meeting cadence",
            },
            {
                "id": "g_axis",
                "label": "Axis Network",
                "type": "Group",
                "description": "Secondary coordination cell",
                "notes": "Cross-border interactions",
            },
        ]
    )

    edges_df = pd.DataFrame(
        [
            {
                "source": "p_alice",
                "target": "i_meridian",
                "relationship_type": "employed_by",
                "description": "Alice appears in payroll summaries",
                "source_ref": "payroll_2023_q2",
            },
            {
                "source": "p_bruno",
                "target": "pl_harbor",
                "relationship_type": "operates_in",
                "description": "Bruno tracked near harbor logistics offices",
                "source_ref": "surveillance_log_17",
            },
            {
                "source": "p_clara",
                "target": "i_cityhall",
                "relationship_type": "advises",
                "description": "Clara listed on advisory committee minutes",
                "source_ref": "minutes_apr_2024",
            },
            {
                "source": "g_tide",
                "target": "p_alice",
                "relationship_type": "coordinates",
                "description": "Group tasks routed through Alice",
                "source_ref": "chat_export_091",
            },
            {
                "source": "g_tide",
                "target": "p_bruno",
                "relationship_type": "coordinates",
                "description": "Bruno receives operational requests",
                "source_ref": "chat_export_094",
            },
            {
                "source": "g_axis",
                "target": "p_clara",
                "relationship_type": "coordinates",
                "description": "Clara contributes strategy memos",
                "source_ref": "memo_chain_22",
            },
            {
                "source": "i_meridian",
                "target": "i_cityhall",
                "relationship_type": "contracts_with",
                "description": "Vendor contract for permit processing",
                "source_ref": "contract_8841",
            },
            {
                "source": "p_alice",
                "target": "p_clara",
                "relationship_type": "communicates_with",
                "description": "Regular planning calls",
                "source_ref": "call_log_week32",
            },
            {
                "source": "p_bruno",
                "target": "g_axis",
                "relationship_type": "reports_to",
                "description": "Bruno provides transport updates",
                "source_ref": "ops_report_11",
            },
            {
                "source": "g_axis",
                "target": "pl_university",
                "relationship_type": "recruits_from",
                "description": "Recruitment outreach near campus",
                "source_ref": "flyer_batch_b",
            },
            {
                "source": "p_clara",
                "target": "pl_university",
                "relationship_type": "visited",
                "description": "Recorded attendance at panel event",
                "source_ref": "event_sheet_53",
            },
            {
                "source": "g_tide",
                "target": "pl_harbor",
                "relationship_type": "meets_at",
                "description": "Recurring meetings in warehouse district",
                "source_ref": "field_note_h12",
            },
        ]
    )

    nodes_df = nodes_df.loc[:, _ordered_columns(nodes_df, REQUIRED_NODE_COLS)]
    nodes_df = nodes_df.sort_values(by=["id"], kind="mergesort").reset_index(drop=True)

    edges_df = edges_df.loc[:, _ordered_columns(edges_df, REQUIRED_EDGE_COLS)]
    edges_df = _sort_sample_edges(edges_df)

    save_workbook(nodes_df, edges_df, path=str(workbook_path))
    return str(workbook_path)
