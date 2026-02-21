import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.validate import validate_data


def _valid_nodes() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["N1", "N2"],
            "label": ["Node 1", "Node 2"],
            "type": ["person", "org"],
            "description": ["desc1", "desc2"],
        }
    )


def _valid_edges() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source": ["N1"],
            "target": ["N2"],
            "relationship_type": ["connected_to"],
            "description": ["link"],
        }
    )


def test_validate_data_returns_empty_list_for_valid_data() -> None:
    assert validate_data(_valid_nodes(), _valid_edges()) == []


def test_validate_data_detects_duplicate_node_id() -> None:
    nodes_df = _valid_nodes()
    nodes_df.loc[1, "id"] = "N1"

    issues = validate_data(nodes_df, _valid_edges())

    duplicate_issues = [issue for issue in issues if "Duplicate node id" in issue["message"]]
    assert duplicate_issues
    assert all(issue["where"] == "nodes" for issue in duplicate_issues)


def test_validate_data_detects_unknown_edge_source() -> None:
    edges_df = _valid_edges()
    edges_df.loc[0, "source"] = "UNKNOWN"

    issues = validate_data(_valid_nodes(), edges_df)

    assert any("Unknown edge source 'UNKNOWN'" in issue["message"] for issue in issues)


def test_validate_data_detects_unknown_edge_target() -> None:
    edges_df = _valid_edges()
    edges_df.loc[0, "target"] = "UNKNOWN"

    issues = validate_data(_valid_nodes(), edges_df)

    assert any("Unknown edge target 'UNKNOWN'" in issue["message"] for issue in issues)


def test_validate_data_detects_missing_source_and_target() -> None:
    edges_df = _valid_edges()
    edges_df.loc[0, "source"] = None
    edges_df.loc[0, "target"] = None

    issues = validate_data(_valid_nodes(), edges_df)

    assert any("Missing edge source" in issue["message"] for issue in issues)
    assert any("Missing edge target" in issue["message"] for issue in issues)
