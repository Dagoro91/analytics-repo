"""Guardrails for LLM-generated SQL: read-only, single statement, row limit."""
import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|copy|pragma|install|load|call|export|import|truncate)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> str:
    """Return a cleaned SELECT statement or raise ValueError."""
    cleaned = (sql or "").strip().rstrip(";").strip()
    if not cleaned:
        raise ValueError("Empty SQL")
    if ";" in cleaned:
        raise ValueError("Multiple statements are not allowed")
    if not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    if FORBIDDEN.search(cleaned):
        raise ValueError("Query contains a forbidden keyword")
    return cleaned


def with_limit(sql: str, limit: int = 200) -> str:
    return f"SELECT * FROM ({sql}) AS q LIMIT {int(limit)}"
