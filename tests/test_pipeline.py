"""Runs after `dbt build`: verifies the Gold layer exists and the evaluation SQL is valid."""
from ai.evaluate import check_expected
from ai.text2sql import run_sql


def test_gold_tables_are_not_empty():
    for table in ("gold_monthly_sales", "gold_top_customers", "gold_supplier_performance"):
        assert run_sql(f"SELECT count(*) FROM gold.{table}")[0][0] > 0


def test_expected_queries_run():
    check_expected()
