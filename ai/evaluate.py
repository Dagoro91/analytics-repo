"""Evaluate Text-to-SQL accuracy with and without RAG context.

Usage:
  python -m ai.evaluate                  # run the LLM on all questions, both modes
  python -m ai.evaluate --check-expected # only verify that the expected SQL runs (no LLM)
"""
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from ai.text2sql import generate_sql, run_sql

QUESTIONS = Path("eval/questions.json")


def normalize(rows: list[tuple]) -> list[tuple]:
    def cell(v):
        if isinstance(v, (Decimal, float)):
            return round(float(v), 2)
        if isinstance(v, (date, datetime)):
            return str(v)
        return v

    return sorted((tuple(cell(v) for v in row) for row in rows), key=lambda r: [str(x) for x in r])


def check_expected() -> None:
    for q in json.loads(QUESTIONS.read_text()):
        rows = run_sql(q["expected_sql"])
        assert rows, f"Expected SQL returned no rows for question {q['id']}"
    print("All expected queries run and return rows.")


def evaluate() -> None:
    questions = json.loads(QUESTIONS.read_text())
    summary, details = {}, []
    for mode, use_rag in (("baseline (names only)", False), ("RAG (documented schema)", True)):
        correct = 0
        for q in questions:
            expected = normalize(run_sql(q["expected_sql"]))
            try:
                sql = generate_sql(q["question"], use_rag)
                ok = normalize(run_sql(sql)) == expected
            except Exception as exc:  # generation or execution failure counts as wrong
                sql, ok = f"ERROR: {exc}", False
            correct += ok
            details.append({"mode": mode, "id": q["id"], "ok": ok, "sql": sql})
        summary[mode] = (correct, len(questions))
    lines = ["| Mode | Correct | Accuracy |", "|---|---|---|"]
    for mode, (c, n) in summary.items():
        lines.append(f"| {mode} | {c}/{n} | {c / n:.0%} |")
    Path("eval/results.md").write_text("\n".join(lines) + "\n")
    Path("eval/results.json").write_text(json.dumps(details, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    check_expected() if "--check-expected" in sys.argv else evaluate()
