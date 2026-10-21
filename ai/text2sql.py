"""Text-to-SQL over the Gold layer with a local LLM (Ollama) and optional RAG context."""
import os
import re
import sys

import duckdb
import requests

from ai.context import baseline_context, rag_context
from ai.sql_guard import validate_sql, with_limit

DB_PATH = "data/warehouse.duckdb"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

PROMPT = """You are a careful analytics engineer. Write ONE DuckDB SQL SELECT query that answers the question.
Use only the tables below, always with the gold. schema prefix. Return only the SQL, no explanation.

{context}

Question: {question}
SQL:"""


def extract_sql(text: str) -> str:
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return (match.group(1) if match else text).strip()


def generate_sql(question: str, use_rag: bool = True) -> str:
    context = rag_context(question) if use_rag else baseline_context()
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": PROMPT.format(context=context, question=question),
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=300,
    )
    response.raise_for_status()
    return extract_sql(response.json()["response"])


def run_sql(sql: str, limit: int = 200) -> list[tuple]:
    safe = validate_sql(sql)
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return con.execute(with_limit(safe, limit)).fetchall()
    finally:
        con.close()


def ask(question: str, use_rag: bool = True) -> tuple[str, list[tuple]]:
    sql = generate_sql(question, use_rag)
    return sql, run_sql(sql)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sql, rows = ask(" ".join(args), use_rag="--no-rag" not in sys.argv)
    print(sql)
    for row in rows:
        print(row)
