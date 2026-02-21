"""Utilities for generating a starter workbook with sample graph data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.io_excel import save_workbook


def create_sample_workbook(path: str = "data/data.xlsx") -> str:
    """Create a starter workbook at path and return the created file path."""
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

    save_workbook(nodes_df, edges_df, path=str(workbook_path))
    return str(workbook_path)
