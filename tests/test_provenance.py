import pytest

pytest.importorskip('pandas')
import pandas as pd

from app.provenance import ensure_metadata_columns, is_valid_optional_date, parse_optional_confidence


def test_optional_date_validation() -> None:
    assert is_valid_optional_date('')
    assert is_valid_optional_date('2024-12-31')
    assert not is_valid_optional_date('2024-1-01')
    assert not is_valid_optional_date('31-12-2024')


def test_optional_confidence_validation() -> None:
    assert parse_optional_confidence('') == (True, '')
    assert parse_optional_confidence(0) == (True, 0.0)
    assert parse_optional_confidence('0.8') == (True, 0.8)
    assert parse_optional_confidence(1) == (True, 1.0)
    assert parse_optional_confidence(-0.1) == (False, '')
    assert parse_optional_confidence(1.1) == (False, '')
    assert parse_optional_confidence('high') == (False, '')


def test_ensure_metadata_columns_creates_columns_on_first_use() -> None:
    nodes_df = pd.DataFrame({'id': ['N1'], 'label': ['Node 1']})

    updated = ensure_metadata_columns(nodes_df)

    assert 'source_ref' in updated.columns
    assert 'date' in updated.columns
    assert 'confidence' in updated.columns
    assert updated.at[0, 'source_ref'] == ''
    assert updated.at[0, 'date'] == ''
    assert updated.at[0, 'confidence'] == ''
