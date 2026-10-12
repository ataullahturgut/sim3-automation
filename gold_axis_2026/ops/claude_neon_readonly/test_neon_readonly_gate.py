"""Unit tests for neon_readonly_gate.decide (run: python3 test_neon_readonly_gate.py)."""
from neon_readonly_gate import decide

T = "mcp__Neon__run_sql_transaction"
RO = "SET TRANSACTION READ ONLY"


def p(stmts, tool=T, **kw):
    return {"tool_name": tool, "tool_input": {"sql_statements": stmts, **kw}}


ALLOW = [
    p([RO, "SELECT 1"]),
    p([RO, "select ts_event, close from x where ts_event >= '2023-01-01' order by 1"],
      project_id="winter-art-94880101"),
    p([RO, "WITH a AS (SELECT 1 AS v) SELECT v FROM a;"]),
    p([RO, "SELECT created_at, update_count FROM t"]),  # identifiers containing keywords
    p([RO, "SELECT 'drop table x' AS s"]),               # keyword only inside a literal
    p([RO, "SHOW transaction_read_only"]),
    p([RO, "SELECT CASE WHEN x > 0 THEN 1 ELSE 0 END AS s FROM t"]),
]
ASK = [
    p(["SELECT 1"]),                                      # no read-only header
    p([RO]),                                              # nothing to run
    p([RO, "SELECT 1"], tool="mcp__Neon__run_sql"),
    p([RO, "SELECT 1"], project_id="other-project"),
    p([RO, "SELECT 1"], branch_id="br-x"),
    p([RO, "COMMIT", "DROP TABLE t"]),
    p([RO, "SELECT 1; DROP TABLE t"]),
    p([RO, "WITH d AS (DELETE FROM t RETURNING *) SELECT * FROM d"]),
    p([RO, "SELECT * INTO new_t FROM t"]),
    p([RO, "SELECT pg_terminate_backend(123)"]),
    p([RO, "SELECT * FROM t FOR UPDATE"]),
    p([RO, "EXPLAIN ANALYZE SELECT 1"]),
    p([RO, "SELECT $$x$$"]),
    p([RO, "SELECT E'\\'' "]),
    p([RO, "SELECT 'unterminated"]),
    p([RO, "SELECT nextval('s')"]),
    p([RO, "SELECT set_config('transaction_read_only','off',false)"]),
    p(["SET TRANSACTION READ WRITE", "SELECT 1"]),
    p([RO, "INSERT INTO t VALUES (1)"]),
    p([RO, "CREATE TABLE gold_research_r99_x_v1 AS SELECT 1"]),
]
fails = [c for c in ALLOW if not decide(c)] + [c for c in ASK if decide(c)]
for c in fails:
    print("FAIL", c)
print(f"{len(ALLOW)} allow + {len(ASK)} ask cases; failures={len(fails)}")
raise SystemExit(1 if fails else 0)
