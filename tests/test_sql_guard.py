import pytest

from ai.sql_guard import validate_sql, with_limit


def test_accepts_select_and_cte():
    assert validate_sql("SELECT 1;") == "SELECT 1"
    assert validate_sql("WITH a AS (SELECT 1) SELECT * FROM a").startswith("WITH")


@pytest.mark.parametrize(
    "bad",
    ["DROP TABLE gold.gold_monthly_sales", "SELECT 1; SELECT 2", "INSERT INTO t VALUES (1)", "", "COPY t TO 'x.csv'"],
)
def test_rejects_unsafe_sql(bad):
    with pytest.raises(ValueError):
        validate_sql(bad)


def test_with_limit_wraps_query():
    assert with_limit("SELECT 1", 5) == "SELECT * FROM (SELECT 1) AS q LIMIT 5"
