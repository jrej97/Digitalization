import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.crud_nodes import can_delete_node, edge_reference_count, is_unique_node_id


def test_is_unique_node_id_for_add() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert is_unique_node_id(nodes_df, 'N3')
    assert not is_unique_node_id(nodes_df, 'N1')


def test_is_unique_node_id_excludes_current_row_for_edit() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert is_unique_node_id(nodes_df, 'N1', exclude_index=0)
    assert not is_unique_node_id(nodes_df, 'N2', exclude_index=0)


def test_can_delete_node_blocks_referenced_nodes() -> None:
    edges_df = pd.DataFrame({'source': ['N1', 'N2'], 'target': ['N3', 'N1']})

    assert edge_reference_count(edges_df, 'N1') == 2
    assert can_delete_node(edges_df, 'N1') == (False, 2)
    assert can_delete_node(edges_df, 'N4') == (True, 0)
