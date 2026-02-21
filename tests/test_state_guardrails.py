from app.state_guardrails import is_dirty, mark_clean, mark_dirty


def test_dirty_flag_transitions() -> None:
    mark_clean()
    assert is_dirty() is False

    mark_dirty()
    assert is_dirty() is True

    mark_clean()
    assert is_dirty() is False
