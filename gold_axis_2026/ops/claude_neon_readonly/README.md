# Claude Code — Gold Control Neon read-only approval (PROPOSAL, install manually)

Claude Code's safety classifier refuses to let Claude write its own permission files
(`.claude/settings.json`, `.claude/hooks/`). These files are therefore only a proposal;
the user installs them.

## What it does

| Call | Result |
|---|---|
| `mcp__Neon__get_database_tables`, `mcp__Neon__describe_table_schema` | allowed without prompt (metadata only) |
| `mcp__Neon__run_sql_transaction` whose first statement is `SET TRANSACTION READ ONLY`, followed only by SELECT/WITH/SHOW/EXPLAIN statements that pass the lexical filter, Gold Control project, default branch | allowed without prompt |
| `mcp__Neon__run_sql`, any write, DDL, migration, branch/project/role tool, anything else | **unchanged: normal permission prompt** |

Two independent locks: Postgres enforces the read-only transaction (verified 2026-10-12:
`CREATE TEMP TABLE` inside it failed with "cannot execute CREATE TABLE in a read-only
transaction"), and the hook additionally refuses transaction control, side-effecting
functions, `INTO`, `FOR UPDATE`, dollar quoting, etc. (`test_neon_readonly_gate.py`: 7
allow / 20 ask cases pass). No `bypassPermissions`, no server-wide `mcp__Neon` allow.

Caveat: the connector currently authenticates as `neondb_owner` in Neon write mode.
The hook makes *auto-approved* calls read-only; it does not make the connector itself
read-only. A Neon-side read-only grant requires reconnecting the claude.ai Neon
connector with `https://mcp.neon.tech/mcp?readonly=true&projectId=winter-art-94880101`
(OAuth, user action). A CLI-added `gold_neon_ro` server cannot connect from the cloud
container (`ERR_PROXY_TUNNEL`: environment network policy blocks `mcp.neon.tech`, and the
OAuth browser step is unavailable there), so the claude.ai connector is the route.

## Install (user)

```
mkdir -p .claude/hooks
cp gold_axis_2026/ops/claude_neon_readonly/neon_readonly_gate.py .claude/hooks/
cp gold_axis_2026/ops/claude_neon_readonly/settings.json.proposed .claude/settings.json
git add .claude && git commit -m "Claude Code: Gold Control Neon read-only auto-approval"
```

Cloud sessions read `.claude/settings.json` from the checked-out branch (repository
default branch `main` unless another is chosen), so the file must be on that branch.
Hooks are loaded at session start; open a new session after installing.
