# ChatGPT Execution Runbook

## Source of truth

The authoritative project is always:

- repository: `ataullahturgut/sim3-automation`
- branch: `gold-r4-direction-engine`
- path: `gold_axis_2026/r4_1/`

ChatGPT must not silently use a locally modified copy as the authoritative model.

## Standard execution sequence from ChatGPT

1. Read the current branch head / relevant file SHAs from GitHub.
2. Fetch the exact code/config required for the requested run.
3. Materialize those exact files into the temporary execution environment.
4. Load only timestamp-valid input data for the requested as-of date.
5. Run the frozen engine without changing thresholds or rules.
6. Report:
   - GitHub branch and commit SHA used,
   - as-of timestamp,
   - data-source lineage,
   - monthly VW frozen forecast,
   - 3M direction,
   - Fast / Slow,
   - Level Emergency,
   - Reversal Emergency,
   - GVZ cap / panic,
   - Macro Event status if available,
   - BOCPD context if available,
   - final classification,
   - any BLOCKED / NOT_RECOVERED fields.
7. If code is changed, commit the change back to GitHub first and then rerun from the new GitHub commit.

## Anti-drift rule

Results shown in chat must correspond to a specific GitHub commit. A result produced from uncommitted experimental code must be explicitly labeled `LOCAL_EXPERIMENT_NOT_SOURCE_OF_TRUTH`.

## User-facing trigger

When the user says phrases such as:

- `modeli çalıştır`
- `bugünkü altın sinyalini çalıştır`
- `28 Ağustos'u replay et`
- `R4.1'i çalıştır`

ChatGPT should treat that as a request to execute the current GitHub source-of-truth version and show the resulting state in chat.
