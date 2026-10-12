#!/usr/bin/env python3
"""PROPOSED PreToolUse gate (install manually): auto-approve only
database-enforced read-only Neon queries on the Gold Control project.

Auto-allow (no prompt) ONLY when ALL of these hold:
  * tool is mcp__Neon__run_sql_transaction;
  * project_id is absent or equals the Gold Control project; no branch_id;
  * first statement is exactly ``SET TRANSACTION READ ONLY`` (Postgres then
    rejects any write inside the transaction);
  * every remaining statement also passes a conservative lexical filter
    (SELECT/WITH/SHOW/EXPLAIN/TABLE/VALUES only, no transaction control,
    no side-effecting functions, no literals that could hide tokens).

Anything else prints nothing, so Claude Code's normal permission prompt
applies. This hook never denies and never widens any other tool.
"""
import json
import re
import sys

GOLD_PROJECT_ID = "winter-art-94880101"
MAX_STATEMENTS = 20
MAX_CHARS = 50_000

ALLOWED_START = re.compile(r"^\s*\(?\s*(select|with|show|explain|table|values)\b", re.I)
FORBIDDEN_WORDS = re.compile(
    r"\b("
    r"insert|update|delete|merge|upsert|drop|alter|create|truncate|grant|revoke|"
    r"copy|call|do|vacuum|analyze|analyse|cluster|reindex|refresh|lock|comment|"
    r"security|set|reset|begin|start|commit|end|abort|rollback|savepoint|release|"
    r"prepare|execute|deallocate|listen|notify|unlisten|discard|checkpoint|load|"
    r"import|into|returning|nextval|setval|set_config|dblink|dblink_exec|"
    r"lo_import|lo_export|lo_unlink|lo_create|lo_put|lo_from_bytea|"
    r"pg_terminate_backend|pg_cancel_backend|pg_reload_conf|pg_rotate_logfile|"
    r"pg_read_file|pg_read_binary_file|pg_ls_dir|pg_stat_file|pg_sleep|"
    r"pg_sleep_for|pg_sleep_until|pg_advisory_lock|pg_advisory_xact_lock|"
    r"pg_try_advisory_lock|pg_try_advisory_xact_lock|pg_notify|"
    r"pg_logical_emit_message|pg_switch_wal|pg_create_restore_point|txid_current"
    r")\b",
    re.I,
)
READ_ONLY_HEADER = re.compile(r"^\s*set\s+transaction\s+read\s+only\s*;?\s*$", re.I)


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def statement_is_safe(sql) -> bool:
    if not isinstance(sql, str) or len(sql) > MAX_CHARS:
        return False
    # Backslashes (E-strings) and dollar quoting can hide tokens: never auto-allow.
    if "\\" in sql or re.search(r"\$[A-Za-z_]*\$", sql):
        return False
    body = strip_comments(sql)
    body = re.sub(r"'(?:[^']|'')*'", "''", body)
    body = re.sub(r'"(?:[^"]|"")*"', '""', body)
    if body.replace("''", "").count("'") or body.replace('""', "").count('"'):
        return False  # unbalanced quoting
    body = body.strip()
    if body.endswith(";"):
        body = body[:-1]
    if ";" in body:
        return False  # exactly one statement per array element
    if not ALLOWED_START.match(body):
        return False
    return not FORBIDDEN_WORDS.search(body)


def decide(payload: dict) -> bool:
    if payload.get("tool_name") != "mcp__Neon__run_sql_transaction":
        return False
    tool_input = payload.get("tool_input") or {}
    if tool_input.get("project_id") not in (None, GOLD_PROJECT_ID):
        return False
    if tool_input.get("branch_id") not in (None, ""):
        return False
    stmts = tool_input.get("sql_statements")
    if not isinstance(stmts, list) or not 2 <= len(stmts) <= MAX_STATEMENTS:
        return False
    if not isinstance(stmts[0], str) or not READ_ONLY_HEADER.match(strip_comments(stmts[0])):
        return False
    return all(statement_is_safe(s) for s in stmts[1:])


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if decide(payload):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason":
                    "Gold Control read-only: SET TRANSACTION READ ONLY + SELECT-only lexical filter",
            }
        }))


if __name__ == "__main__":
    main()
