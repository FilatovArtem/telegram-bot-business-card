from bot.handlers._utils import cb_int


def test_cb_int_valid_extracts_integer() -> None:
    assert cb_int("cat:5", 1) == 5


def test_cb_int_letter_value_returns_none() -> None:
    assert cb_int("cat:abc", 1) is None


def test_cb_int_empty_part_returns_none() -> None:
    assert cb_int("cat:", 1) is None


def test_cb_int_index_out_of_bounds_returns_none() -> None:
    # "cat" has only 1 part at index 0, index 1 does not exist
    assert cb_int("cat", 1) is None


def test_cb_int_nested_path_extracts_correct_part() -> None:
    # "admin:status:42:confirmed" → idx=2 → 42
    assert cb_int("admin:status:42:confirmed", 2) == 42
