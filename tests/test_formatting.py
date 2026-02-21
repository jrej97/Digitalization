from app.formatting import format_inspector_rows


def test_format_inspector_rows_node_includes_core_and_sorted_extra() -> None:
    rows = format_inspector_rows(
        'node',
        {
            'label': 'Alice',
            'id': 'N1',
            'type': 'person',
            'description': None,
            'zeta': 5,
            'alpha': 'first',
        },
    )

    assert rows[:4] == [
        ('id', 'N1'),
        ('label', 'Alice'),
        ('type', 'person'),
        ('description', ''),
    ]
    assert rows[4:] == [('alpha', 'first'), ('zeta', '5')]


def test_format_inspector_rows_edge_truncates_large_values() -> None:
    long_text = 'x' * 250
    rows = format_inspector_rows(
        'edge',
        {
            'id': 'E1',
            'source': 'N1',
            'target': 'N2',
            'relationship_type': 'knows',
            'description': 'desc',
            'notes': long_text,
        },
    )

    notes_row = dict(rows)['notes']
    assert len(notes_row) == 203
    assert notes_row.endswith('...')


def test_format_inspector_rows_unknown_kind_is_empty() -> None:
    assert format_inspector_rows('none', {'id': 'X'}) == []
