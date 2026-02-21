import pytest

pytest.importorskip("pandas")
import pandas as pd

from app.crud_edges import can_add_or_edit_edge


def test_can_add_or_edit_edge_requires_source_target_and_relationship_type() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert can_add_or_edit_edge(nodes_df, '', 'N2', 'knows') == (False, 'source is required')
    assert can_add_or_edit_edge(nodes_df, 'N1', '', 'knows') == (False, 'target is required')
    assert can_add_or_edit_edge(nodes_df, 'N1', 'N2', '') == (False, 'relationship_type is required')


def test_can_add_or_edit_edge_checks_source_and_target_existence() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert can_add_or_edit_edge(nodes_df, 'N9', 'N2', 'knows') == (False, "source 'N9' does not exist")
    assert can_add_or_edit_edge(nodes_df, 'N1', 'N9', 'knows') == (False, "target 'N9' does not exist")


def test_can_add_or_edit_edge_blocks_self_loop() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert can_add_or_edit_edge(
        nodes_df,
        'N1',
        'N1',
        'knows',
    ) == (False, 'source and target must be different (self-loops are not allowed yet)')


def test_can_add_or_edit_edge_accepts_valid_edge() -> None:
    nodes_df = pd.DataFrame({'id': ['N1', 'N2']})

    assert can_add_or_edit_edge(nodes_df, 'N1', 'N2', 'knows') == (True, '')
