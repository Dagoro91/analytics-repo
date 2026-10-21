from decimal import Decimal

from ai.evaluate import exact_match, tolerant_match


def test_extra_column_is_tolerated_but_not_exact():
    expected = [("Customer#001",)]
    generated = [("Customer#001", Decimal("10.50"))]
    assert not exact_match(expected, generated)
    assert tolerant_match(expected, generated)


def test_reordered_columns_are_tolerated():
    assert tolerant_match([("EUROPE", 5.0)], [(5.0, "EUROPE")])


def test_wrong_values_are_rejected():
    assert not tolerant_match([("A",)], [("B", 1)])


def test_different_row_counts_are_rejected():
    assert not tolerant_match([("A",), ("B",)], [("A", 1)])


def test_row_order_is_ignored():
    assert exact_match([(1,), (2,)], [(2,), (1,)])


def test_numbers_are_rounded_to_two_decimals():
    assert exact_match([(Decimal("1.004"),)], [(1.0,)])
