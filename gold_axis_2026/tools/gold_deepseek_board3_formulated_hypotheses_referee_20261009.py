"""Limited-cost DeepSeek scientific second-opinion bridge for gold session research.

Only explicitly allowlisted public-safe aggregate research brief is supplied.
Never sends Neon rows, proprietary source bars, credentials, API secrets, user
information, database/schema internals, repository contents or raw backtests.
No model-generated code is run and no trades are placed.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import time
import urllib.error
import urllib.request

AX = Path(__file__).resolve().parents[1]
SAFE_BRIEF = AX / "GOLD_MULTIDISCIPLINARY_THREE_MECHANISM_PREREG_20261009.md"
STEM = AX / "GOLD_DEEPSEEK_BOARD3_HYPOTHESES_REFEREE_20261009"
BASE = "https://api.deepseek.com"
MODEL = "deepseek-flash"       # Official latest V4.1 Flash, deliberately cheap first pass
MAX_COMPLETION_TOKENS = 2600
MAX_REQUESTS_PER_RUN = 2      # Excludes GET /models and retries due solely to 502-504
MAX_BRIEF_BYTES = 14000
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

SYSTEM = (
    "You are a mathematically rigorous and independent scientific researcher "
    "working on XAU/USD causal forecast experiments. Not an investment adviser. "
    "Your task is to critique the established failed models and propose "
    "genuinely new, falsifiable signed-return mechanisms, with exact as-of "
    "information timing. Do NOT merely restate CBR, PRAMV, HGB, consensus, "
    "conformal confidence, old price-volatility labels, or a generic ensemble. "
    "Avoid unverifiable numerical gains, invented citations, future-release "
    "surprises, leaking current target price, unstated source availability "
    "or promises of profitable bank execution. Explicitly separate a hypothesis "
    "from demonstrated experimental evidence. Output final answer ONLY."
)

def call(path: str, key: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE + path, data=body,
        headers={**HEADERS, "Authorization": "Bearer " + key},
        method="GET" if body is None else "POST",
    )
    for retry in range(3):
        try:
            with urllib.request.urlopen(request, timeout=75) as response:
                if response.status != 200:
                    raise RuntimeError("DEEPSEEK_HTTP_NON200")
                item = json.loads(response.read(700_000).decode("utf-8"))
            if not isinstance(item, dict):
                raise RuntimeError("DEEPSEEK_MALFORMED_JSON")
            return item
        except urllib.error.HTTPError as exc:
            # Never print error body: provider payload can echo private request.
            if exc.code in (502, 503, 504) and retry < 2:
                print("DEEPSEEK_TRANSIENT_HTTP_RETRY:", exc.code, retry + 1, flush=True)
                time.sleep(2 if retry == 0 else 5)
                continue
            raise RuntimeError("DEEPSEEK_HTTP_STATUS_" + str(exc.code)) from None
        except (socket.timeout, TimeoutError, urllib.error.URLError):
            raise RuntimeError("DEEPSEEK_PROVIDER_TIMEOUT_OR_NETWORK_UNAVAILABLE") from None
    raise RuntimeError("DEEPSEEK_TRANSIENT_RETRY_LIMIT")

def model_authorized(key: str) -> bool:
    response = call("/models", key)
    names = [str(row.get("id")) for row in response.get("data", []) if isinstance(row, dict)]
    if MODEL not in names:
        raise RuntimeError("DEEPSEEK_FLASH_NOT_LISTED_FOR_THIS_KEY")
    return True

def generate(key: str, history: list[dict]) -> tuple[str, dict]:
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM}] + history,
        "stream": False,
        "max_tokens": MAX_COMPLETION_TOKENS,
        # Nonthinking is an intentional cheap first experiment; mathematically
        # rich reasoning mode requires separate cost-authorization decision.
        "thinking": {"type": "disabled"},
    }
    response = call("/chat/completions", key, payload)
    choices = response.get("choices") or []
    if not choices:
        raise RuntimeError("DEEPSEEK_EMPTY_CHOICES")
    first = choices[0]
    finish = str(first.get("finish_reason", ""))
    message = first.get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or len(content.strip()) < 900 or finish != "stop":
        raise RuntimeError("DEEPSEEK_OUTPUT_INCOMPLETE_OR_TRUNCATED")
    if len(content) > 20000:
        raise RuntimeError("DEEPSEEK_OUTPUT_TOO_LONG_REJECTED")
    u = response.get("usage") or {}
    usage = {k: int(u[k]) for k in ("prompt_tokens", "completion_tokens", "total_tokens")
             if isinstance(u.get(k), int)}
    return content, usage

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "research"], default="research")
    mode = parser.parse_args().mode
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY_GITHUB_SECRET_MISSING")
    if any(x.isspace() for x in key):
        raise RuntimeError("DEEPSEEK_API_KEY_FORMAT_INVALID")
    if not SAFE_BRIEF.is_file() or not SAFE_BRIEF.resolve().is_relative_to(AX.resolve()):
        raise RuntimeError("DEEPSEEK_ALLOWLISTED_SAFE_BRIEF_MISSING")
    safe_bytes = SAFE_BRIEF.read_bytes()
    if not 2000 <= len(safe_bytes) <= MAX_BRIEF_BYTES:
        raise RuntimeError("DEEPSEEK_SAFE_BRIEF_WRONG_SIZE")
    safe_text = safe_bytes.decode("utf-8")
    safe_hash = hashlib.sha256(safe_bytes).hexdigest()
    if not model_authorized(key):
        raise RuntimeError("DEEPSEEK_AUTH_UNAVAILABLE")
    print("DEEPSEEK_API_AUTH_MODEL_LIST_PASS model=" + MODEL, flush=True)
    if mode == "smoke":
        receipt = {"status": "DEEPSEEK_API_KEY_AND_MODEL_AUTHENTICATED_NO_CONTENT_CALL",
                   "model": MODEL, "generation_calls": 0,
                   "safe_brief_sha256": safe_hash}
        Path(str(STEM) + "_CONNECTION.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return

    question = (
        "You are one hostile expert on an INDEPENDENT RESEARCH BOARD. "
        "GPT-6 has already researched literature, checked the manifest, "
        "and preregistered EXACTLY THREE testable signed XAU state mechanisms "
        "(S1 spot semivariance sign, S2 high/low range rejection, S3 shock "
        "concentration and reversal). Do NOT propose alternate models. "
        "Review each exact formula and price-observation clock against "
        "the two forecast windows 09 Istanbul→17 and 17→next09. "
        "Spot the strongest scientific objection, any hidden future target "
        "price leakage, and sample-selection / fake alpha risk. "
        "S1 has analogue in OPTIONS semivariance, not proof for spot; "
        "S2 range-end reversal could be trend continuation instead; "
        "S3 a big jump might propagate, not revert. Criticize thresholds "
        "and sign orientation frozen without data. Indicate if any study "
        "would exactly duplicate prior PRAMV, early half-hour RFR or "
        "proposed but NOT RUN TURN/CAVS. Decide separately: retain as "
        "low-cost negative-control experiment or reject conceptually. "
        "State precise same-date paired decision rules and the strongest "
        "falsification, not forecast performance numbers. "
        "At most 1250 words. Exact aggregate-only author prereg:\\n\\n"
        + safe_text
    )
    first, use1 = generate(key, [{"role": "user", "content": question}])
    rebuttal = (
        "Now as a second adversarial expert, find mistakes in the prior "
        "review and determine whether these three experiments justify a "
        "minimal multi-path audit BEFORE expanding architecture. "
        "Give a hard implementation and integrity gate: continuous 17 "
        "M15 close observations before each issue and no filled "
        "overnight missed candles, as-of 16:45 or08:45, equal full-date "
        "samples, exact 2023/24 development vs already inspected 2025. "
        "Suggest how to compare to last1h and last4h momentum and "
        "what significance would be misleading across six tests. "
        "If one mechanism is scientifically redundant, say REJECT, "
        "not optimize on 2025 outcomes. Finish with a decisive explicit "
        "go/no-go per candidate. At most 900 words, no invented scores."
    )
    second, use2 = generate(key, [
        {"role": "user", "content": question},
        {"role": "assistant", "content": first},
        {"role": "user", "content": rebuttal}
    ])
    result = (
        "# DeepSeek independent scientific research exchange (unverified hypotheses)\n\n"
        "This is untrusted external LLM output. NO market backtest has been run by "
        "DeepSeek; mathematical claims and literature must be checked separately. "
        "Not trading instructions, an audited model result, or a guaranteed improvement.\n\n"
        "Model: " + MODEL + "\n\nBrief SHA256: " + safe_hash + "\n\n"
        "## Technical referee 1: proposed three fixed hypotheses\n\n" + first +
        "\n\n## Technical referee 2: independent adversarial critique\n\n"
        + second + "\n"
    )
    Path(str(STEM) + "_REVIEW.md").write_text(result, encoding="utf-8")
    state = {
        "status": "DEEPSEEK_COMPLETE_TWO_ROUND_INDEPENDENT_RESEARCH_TEXT",
        "model": MODEL, "thinking_mode": "disabled_low_cost_first_trial",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "safe_brief_path": SAFE_BRIEF.name, "safe_brief_sha256": safe_hash,
        "content_calls": MAX_REQUESTS_PER_RUN,
        "round1_output_chars": len(first), "round2_output_chars": len(second),
        "round1_usage": use1, "round2_usage": use2,
        "never_transmitted": "raw quote rows, proprietary private code, secrets, credentials, private repository files",
        "no_generated_model_execution": True, "no_bank_trades": True,
        "no_claim_of_forecasting_improvement": True,
        "external_research_needs_independent_validation": True,
        "pricing_not_certified_free": True,
    }
    Path(str(STEM) + "_RESULT.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fail = Path(str(STEM) + "_FAILURE_QC.json")
    if fail.exists():
        fail.unlink()
    print("DEEPSEEK_TWO_TURN_INDEPENDENT_SCIENCE: PASS", flush=True)
    print("DEEPSEEK_VISIBLE_OUTPUT_CHARACTERS:", len(first), len(second), flush=True)
    print("DEEPSEEK_TOKEN_USAGE:", use1, use2, flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        why = str(e)
        if not why.startswith("DEEPSEEK_"):
            why = type(e).__name__ + "_UNEXPECTED_FAILURE"
        fail = {"status": "DEEPSEEK_CONNECTOR_FAIL_CLOSED",
                "safe_reason": why[:120], "never_log_secret": True,
                "research_completed": False}
        Path(str(STEM) + "_FAILURE_QC.json").write_text(
            json.dumps(fail, indent=2) + "\n", encoding="utf-8")
        print("DEEPSEEK_FAIL_CLOSED:", fail["safe_reason"], flush=True)
        raise SystemExit(1)
