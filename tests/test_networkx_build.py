import pytest

pytest.importorskip("pandas")
import pandas as pd

nx = pytest.importorskip("networkx")

from app.graph_build import build_networkx_graph


def test_build_networkx_graph_type_and_attributes() -> None:
    nodes_df = pd.DataFrame(
        {
            "id": ["N1", "N2"],
            "label": ["Node 1", "Node 2"],
            "type": ["person", "org"],
            "description": [float("nan"), "Known"],
            "tags": [["x", "y"], {"role": "lead"}],
        }
    )
    edges_df = pd.DataFrame(
        {
            "source": ["N1"],
            "target": ["N2"],
            "relationship_type": ["linked"],
            "description": [float("nan")],
            "weight": [0.9],
            "meta": [{"kind": "tip"}],
        }
    )

    graph = build_networkx_graph(nodes_df, edges_df)

    assert isinstance(graph, nx.MultiGraph)
    assert not graph.is_directed()

    node_data = graph.nodes["N1"]
    assert node_data["label"] == "Node 1"
    assert node_data["type"] == "person"
    assert node_data["description"] == ""
    assert node_data["tags"] == "['x', 'y']"

    edge_data = next(iter(graph.get_edge_data("N1", "N2").values()))
    assert edge_data["relationship_type"] == "linked"
    assert edge_data["description"] == ""
    assert edge_data["weight"] == 0.9
    assert edge_data["meta"] == "{'kind': 'tip'}"


def test_build_networkx_graph_preserves_duplicate_edges() -> None:
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
            "description": ["first", "second"],
        }
    )

    graph = build_networkx_graph(nodes_df, edges_df)

    assert graph.number_of_edges() == 2
    edge_descriptions = sorted(
        edge_attrs["description"] for edge_attrs in graph.get_edge_data("A", "B").values()
    )
    assert edge_descriptions == ["first", "second"]
