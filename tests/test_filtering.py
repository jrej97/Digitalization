import pytest

pytest.importorskip('pandas')
import pandas as pd

from app.filtering import (
    DEFAULT_NODE_TYPE_FILTER,
    DEFAULT_RELATIONSHIP_FILTER,
    DEFAULT_SEARCH_FILTER,
    apply_filters,
    default_filters,
)


def test_default_filters_match_reset_values() -> None:
    assert default_filters() == (
        DEFAULT_NODE_TYPE_FILTER,
        DEFAULT_RELATIONSHIP_FILTER,
        DEFAULT_SEARCH_FILTER,
    )


def test_apply_filters_type_search_and_relationship() -> None:
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2', 'N3'],
            'label': ['Alice', 'Bob', 'Berlin'],
            'type': ['Person', 'Person', 'Place'],
            'description': ['', '', ''],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1', 'N1', 'N2'],
            'target': ['N2', 'N3', 'N3'],
            'relationship_type': ['KNOWS', 'VISITED', 'VISITED'],
            'description': ['', '', ''],
        }
    )

    nodes_f, edges_f = apply_filters(nodes_df, edges_df, 'Person', 'KNOWS', 'ali')

    assert nodes_f['id'].tolist() == ['N1']
    assert edges_f.empty


def test_apply_filters_keeps_only_edges_with_remaining_endpoints() -> None:
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2', 'N3'],
            'label': ['Alice', 'Bob', 'Berlin'],
            'type': ['Person', 'Person', 'Place'],
            'description': ['', '', ''],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1', 'N1', 'N2'],
            'target': ['N2', 'N3', 'N3'],
            'relationship_type': ['KNOWS', 'VISITED', 'VISITED'],
            'description': ['', '', ''],
        }
    )

    nodes_f, edges_f = apply_filters(nodes_df, edges_df, 'All', 'VISITED', 'b')

    assert set(nodes_f['id']) == {'N2', 'N3'}
    assert len(edges_f) == 1
    assert edges_f.iloc[0]['source'] == 'N2'
    assert edges_f.iloc[0]['target'] == 'N3'


def test_apply_filters_default_reset_returns_original_rows() -> None:
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2'],
            'label': ['Alice', 'Bob'],
            'type': ['Person', 'Person'],
            'description': ['', ''],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1'],
            'target': ['N2'],
            'relationship_type': ['KNOWS'],
            'description': [''],
        }
    )

    nodes_f, edges_f = apply_filters(nodes_df, edges_df, *default_filters())

    assert nodes_f['id'].tolist() == ['N1', 'N2']
    assert edges_f[['source', 'target']].to_dict('records') == [{'source': 'N1', 'target': 'N2'}]
