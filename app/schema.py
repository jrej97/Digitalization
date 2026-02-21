"""Schema constants for the Excel workbook."""

SHEET_NODES = "nodes"
SHEET_EDGES = "edges"

REQUIRED_NODE_COLS = ["id", "label", "type", "description"]
REQUIRED_EDGE_COLS = ["source", "target", "relationship_type", "description"]
