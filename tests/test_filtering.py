import pytest

pytest.importorskip('pandas')
import pandas as pd

from app.filtering import apply_filters


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
