import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.graph_build import build_cytoscape_elements


def test_build_cytoscape_elements_counts_and_node_description_default() -> None:
    nodes_df = pd.DataFrame(
        {
            "id": ["N1", "N2"],
            "label": ["Node 1", "Node 2"],
            "type": ["person", "org"],
            "description": [float("nan"), "known"],
            "rank": [1, 2],
        }
    )
    edges_df = pd.DataFrame(
        {
            "source": ["N1"],
            "target": ["N2"],
            "relationship_type": ["linked"],
            "description": [float("nan")],
            "confidence": [0.9],
        },
        index=[10],
    )

    elements = build_cytoscape_elements(nodes_df, edges_df)

    node_elements = [el for el in elements if "label" in el["data"]]
    edge_elements = [el for el in elements if "source" in el["data"]]

    assert len(node_elements) == 2
    assert len(edge_elements) == 1
    assert set(["id", "label", "type", "description"]).issubset(node_elements[0]["data"])
    assert node_elements[0]["data"]["description"] == ""
    assert node_elements[0]["data"]["rank"] == 1
    assert edge_elements[0]["data"]["description"] == ""


def test_build_cytoscape_elements_edge_id_format_and_stability() -> None:
    nodes_df = pd.DataFrame(
        {
            "id": ["A", "B"],
            "label": ["A", "B"],
            "type": ["entity", "entity"],
            "description": ["", ""],
        }
    )
    edges_df = pd.DataFrame(
        {
            "source": ["A", "A"],
            "target": ["B", "B"],
            "relationship_type": ["knows", "knows"],
            "description": ["desc", "desc"],
        },
        index=[5, 7],
    )

    first_build = build_cytoscape_elements(nodes_df, edges_df)
    second_build = build_cytoscape_elements(nodes_df, edges_df)

    first_edge_ids = [el["data"]["id"] for el in first_build if "source" in el["data"]]
    second_edge_ids = [el["data"]["id"] for el in second_build if "source" in el["data"]]

    assert first_edge_ids == ["A__B__knows__5", "A__B__knows__7"]
    assert second_edge_ids == first_edge_ids
