"""Generate the Bronze layer: raw TPC-H tables inside DuckDB (no downloads, no accounts)."""
import sys
from pathlib import Path

import duckdb

TABLES = ["customer", "orders", "lineitem", "supplier", "nation", "region", "part", "partsupp"]


def main(scale_factor: float = 0.1, db_path: str = "data/warehouse.duckdb") -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db_path)
    con.execute("INSTALL tpch")
    con.execute("LOAD tpch")
    con.execute(f"CALL dbgen(sf={scale_factor})")
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    for table in TABLES:
        con.execute(f"CREATE OR REPLACE TABLE bronze.{table} AS SELECT * FROM main.{table}")
        con.execute(f"DROP TABLE main.{table}")
    counts = {t: con.execute(f"SELECT count(*) FROM bronze.{t}").fetchone()[0] for t in TABLES}
    print("Bronze layer loaded:", counts)
    con.close()


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 0.1)
