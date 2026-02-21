from pathlib import Path

import pytest

pytest.importorskip('pandas')
import pandas as pd

from app.export import export_summary


def test_export_summary_writes_markdown_with_counts_and_extras(tmp_path: Path) -> None:
    nodes_df = pd.DataFrame(
        {
            'id': ['N1', 'N2', 'N3'],
            'label': ['Alice', 'Berlin', 'Org X'],
            'type': ['Person', 'Place', 'Institution'],
            'description': ['', '', ''],
            'alias': ['A', '', 'X'],
        }
    )
    edges_df = pd.DataFrame(
        {
            'source': ['N1', 'N1'],
            'target': ['N2', 'N3'],
            'relationship_type': ['VISITED', 'AFFILIATED_WITH'],
            'description': ['', ''],
            'weight': [1, 2],
        }
    )

    out_path = tmp_path / 'EXPORT_SUMMARY.md'
    exported_path = Path(export_summary(nodes_df, edges_df, out_path=str(out_path)))

    assert exported_path.exists()
    content = exported_path.read_text(encoding='utf-8')
    assert '# Export Summary' in content
    assert 'Node count: 3' in content
    assert 'Edge count: 2' in content
    assert '## Nodes by type' in content
    assert '## Edges by relationship_type' in content
    assert '## Extra columns' in content
    assert 'Nodes extras: alias' in content
    assert 'Edges extras: weight' in content
