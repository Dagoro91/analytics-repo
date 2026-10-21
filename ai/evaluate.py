"""Evaluate Text-to-SQL accuracy with and without RAG context.

Usage:
  python -m ai.evaluate                   # run the LLM on all questions, both modes
  python -m ai.evaluate --rescore         # re-score the SQL saved in eval/results.json (no LLM calls)
  python -m ai.evaluate --check-expected  # only verify that the reference SQL runs (no LLM)

Two scores are reported for every mode:
  exact     the result set equals the reference result set
            (order-insensitive, numbers rounded to 2 decimals)
  tolerant  as above, but the generated query may return extra columns or reorder columns
            (an answer that adds a helpful column is still a correct answer)
"""
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from itertools import permutations
from pathlib import Path

from ai.text2sql import generate_sql, run_sql

QUESTIONS = Path("eval/questions.json")
RESULTS_JSON = Path("eval/results.json")
RESULTS_MD = Path("eval/results.md")
MODES = (("baseline (names only)", False), ("RAG (documented schema)", True))


def normalize(rows: list[tuple]) -> list[tuple]:
    def cell(v):
        if isinstance(v, (Decimal, float)):
            return round(float(v), 2)
        if isinstance(v, (date, datetime)):
            return str(v)
        return v

    return sorted((tuple(cell(v) for v in row) for row in rows), key=lambda r: [str(x) for x in r])


def exact_match(expected: list[tuple], generated: list[tuple]) -> bool:
    return normalize(expected) == normalize(generated)


def tolerant_match(expected: list[tuple], generated: list[tuple]) -> bool:
    """True if the expected columns appear (in any order) inside the generated result."""
    if exact_match(expected, generated):
        return True
    if not expected or not generated or len(expected) != len(generated):
        return False
    m, k = len(expected[0]), len(generated[0])
    if k < m:
        return False
    target = normalize(expected)
    for cols in permutations(range(k), m):
        if normalize([tuple(row[i] for i in cols) for row in generated]) == target:
            return True
    return False


def score(question: dict, sql: str) -> tuple[bool, bool]:
    """Return (exact, tolerant) for one generated query."""
    if sql.startswith("ERROR:"):
        return False, False
    expected = run_sql(question["expected_sql"])
    try:
        generated = run_sql(sql)
    except Exception:
        return False, False
    return exact_match(expected, generated), tolerant_match(expected, generated)


def check_expected() -> None:
    for q in json.loads(QUESTIONS.read_text()):
        rows = run_sql(q["expected_sql"])
        assert rows, f"Expected SQL returned no rows for question {q['id']}"
    print("All expected queries run and return rows.")


def write_report(details: list[dict]) -> None:
    modes = list(dict.fromkeys(d["mode"] for d in details))
    lines = ["| Mode | Exact match | Ignoring extra columns |", "|---|---|---|"]
    for mode in modes:
        rows = [d for d in details if d["mode"] == mode]
        n = len(rows)
        e = sum(d["exact"] for d in rows)
        t = sum(d["tolerant"] for d in rows)
        lines.append(f"| {mode} | {e}/{n} ({e / n:.0%}) | {t}/{n} ({t / n:.0%}) |")
    RESULTS_MD.write_text("\n".join(lines) + "\n")
    RESULTS_JSON.write_text(json.dumps(details, indent=2))
    print("\n".join(lines))


def evaluate() -> None:
    questions = json.loads(QUESTIONS.read_text())
    details = []
    for mode, use_rag in MODES:
        for q in questions:
            try:
                sql = generate_sql(q["question"], use_rag)
            except Exception as exc:  # generation failure counts as wrong
                sql = f"ERROR: {exc}"
            exact, tolerant = score(q, sql)
            details.append({"mode": mode, "id": q["id"], "exact": exact, "tolerant": tolerant, "sql": sql})
    write_report(details)


def rescore() -> None:
    """Re-score the SQL saved in eval/results.json without calling the model again."""
    questions = {q["id"]: q for q in json.loads(QUESTIONS.read_text())}
    details = []
    for d in json.loads(RESULTS_JSON.read_text()):
        exact, tolerant = score(questions[d["id"]], d["sql"])
        details.append({"mode": d["mode"], "id": d["id"], "exact": exact, "tolerant": tolerant, "sql": d["sql"]})
    write_report(details)


if __name__ == "__main__":
    if "--check-expected" in sys.argv:
        check_expected()
    elif "--rescore" in sys.argv:
        rescore()
    else:
        evaluate()
