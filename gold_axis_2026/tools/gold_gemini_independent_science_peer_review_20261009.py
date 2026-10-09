"""Bounded, opt-in Gemini second-researcher peer-review bridge for XAU/USD.

Security: only the explicit allowlisted EXTERNAL_SAFE_BRIEF is sent to Google;
NEVER repo files, quotes, secrets, URLs, credentials, Neon, or arbitrary globs.
A GitHub Actions secret is read as a header, never echoed or persisted.
Gemini text is UNTRUSTED RESEARCH DATA, never executable code or decisions.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import time

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "GOLD_GEMINI_EXTERNAL_SAFE_RESEARCH_BRIEF_20261009.md"
STEM = ROOT / "GOLD_GEMINI_INDEPENDENT_RESEARCH_20261009"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
APPROVED_MODELS = ("gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3-flash")
MAX_REQUESTS = 2
MAX_BRIEF_BYTES = 18000
SOURCE_AUTHORITY = "GOLD_EXECUTION_2026_ACADEMIC_ROOT_CAUSE_AND_INNOVATION_AUTHORITY_20261009.md"

SYSTEM = (
    "Act as a scientifically independent, skeptical quantitative researcher. "
    "You are NOT an investment advisor or a backtest executor. "
    "Be falsifiable, innovative, precise about time-of-information, "
    "prevent source/target leakage and all hindsight. "
    "Do not claim to have run an experiment or cite an article you cannot verify. "
    "No made-up performance statistics. "
    "Old boosting, ordinary logistic, and parameter sweeps are NOT innovations. "
    "Differentiate signed endpoint, first passage and movement magnitude. "
    "Never request credentials or hidden/private market data."
)

def _request(path: str, key: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT + path,
        data=data,
        headers={
            "x-goog-api-key": key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "GoldSessionResearchPeerReview/1.0",
        },
        method="GET" if data is None else "POST",
    )
    # Bounded retry ONLY on Google transient availability errors. Never retry
    # quota, billing, permissions, invalid input, or safety rejections.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=80) as resp:
                if resp.status != 200:
                    raise RuntimeError("GEMINI_HTTP_NON200")
                obj = json.loads(resp.read(600_000).decode("utf-8"))
            if not isinstance(obj, dict):
                raise RuntimeError("GEMINI_RESPONSE_NOT_JSON_OBJECT")
            return obj
        except urllib.error.HTTPError as exc:
            # The server response body may contain request information. Never print it.
            if exc.code in (502, 503, 504) and attempt < 2:
                print("GEMINI_TRANSIENT_PROVIDER_ERROR_RETRY:", exc.code, attempt + 1)
                time.sleep(2 if attempt == 0 else 5)
                continue
            raise RuntimeError(f"GEMINI_HTTP_STATUS_{exc.code}") from None
        except urllib.error.URLError:
            raise RuntimeError("GEMINI_NETWORK_OR_DNS_UNAVAILABLE") from None
    raise RuntimeError("GEMINI_RETRY_LIMIT_EXCEEDED")

def _choose_model(key: str) -> str:
    result = _request("/models?pageSize=500", key)
    allowed = set()
    for x in result.get("models", []):
        methods = x.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            allowed.add(str(x.get("name", "")).removeprefix("models/"))
    for model in APPROVED_MODELS:
        if model in allowed:
            return model
    raise RuntimeError("NO_APPROVED_LOW_COST_FLASH_MODEL_AVAILABLE")

def _generate(key: str, model: str, messages: list[dict], max_out: int = 4400) -> tuple[str, dict]:
    if max_out > 4400 or max_out < 1:
        raise RuntimeError("OUTPUT_TOKEN_CAP_INVALID")
    obj = _request(
        "/models/" + model + ":generateContent",
        key,
        {
            "systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": messages,
            "generationConfig": {
                "temperature": 0.35,
                "maxOutputTokens": max_out,
                "candidateCount": 1,
                # Gemini 2.5 Flash default dynamic thoughts exhausted almost the
                # entire earlier 3100-token cap (123 visible output tokens).
                # Official Gemini docs support finite fixed thinking budgets.
                **({"thinkingConfig": {"thinkingBudget": 512}}
                   if model == "gemini-2.5-flash" else {}),
            },
        },
    )
    fragments = []
    ends = []
    for cand in obj.get("candidates", [])[:1]:
        ends.append(cand.get("finishReason", "UNKNOWN"))
        for part in cand.get("content", {}).get("parts", []):
            if isinstance(part.get("text"), str):
                fragments.append(part["text"])
    text = "\n".join(fragments).strip()
    if len(text) < 950 or ends != ["STOP"]:
        raise RuntimeError("GEMINI_OUTPUT_TRUNCATED_OR_NOT_FINISHED")
    if len(text) > 18000:
        text = text[:18000] + "\n\n[TEXT_TRUNCATED_BY_SOURCE_SAFE_BRIDGE]\n"
    usage = obj.get("usageMetadata", {})
    budget = {k: usage.get(k) for k in (
        "promptTokenCount", "candidatesTokenCount", "totalTokenCount"
    ) if isinstance(usage.get(k), (int, float))}
    return text, budget

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "research"), default="research")
    args = parser.parse_args()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY_REPOSITORY_SECRET_NOT_AVAILABLE")
    if any(c.isspace() for c in key):
        raise RuntimeError("GEMINI_API_KEY_FORMAT_INVALID")
    if not BRIEF.is_file() or not BRIEF.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("EXTERNAL_SAFE_BRIEF_ALLOWLIST_MISSING")
    data = BRIEF.read_bytes()
    if len(data) < 1000 or len(data) > MAX_BRIEF_BYTES:
        raise RuntimeError("EXTERNAL_SAFE_BRIEF_SIZE_INVALID")
    prompt = data.decode("utf-8")
    model = _choose_model(key)
    print("GEMINI_MODELS_LIST_AUTHENTICATED: PASS")
    print("GEMINI_FLASH_MODEL_SELECTED:", model)
    digest = hashlib.sha256(data).hexdigest()
    if args.mode == "smoke":
        report = {"status": "GEMINI_KEY_AUTH_AND_MODEL_LIST_PASS_NO_GENERATION",
                  "model": model, "brief_sha256": digest, "requests": 0,
                  "research_generation_executed": False}
        Path(str(STEM) + "_CONNECTION.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    # Deliberately fixed first question, only the allowlisted aggregate brief.
    initial = (
        "Independently identify THREE genuinely different NEW mathematical "
        "hypotheses, NOT superficial variants of old models, to improve correct "
        "before-09TR DAY and before-17TR OVERNIGHT XAU/USD signed direction, "
        "especially serious negative events. Use ONLY the supplied EXTERNAL-SAFE "
        "aggregate summary. No proprietary input, no real orders. "
        "For each method define causal time-t predictors, exact model/likelihood, "
        "price/first-hit target, falsifiable null, pre-registered experiment, "
        "same-date old-model comparison, 2023-24 DEV/2025 inspected retrospective/"
        "2026 inspected stress and prospective holdout. Identify ALL unknown data "
        "availability as a blocker. Give independent ranked recommendation. "
        "Do not invent papers or results.\n\n"
        "INDEPENDENT EXTERNAL RESEARCH BRIEF:\n" + prompt
    )
    first, usage1 = _generate(
        key, model,
        [{"role": "user", "parts": [{"text": initial}]}],
        4400,
    )
    # Second distinct dialogue turn forces re-examination, no outside datasets.
    challenge = (
        "SCIENTIFIC PEER CHALLENGE (from project lead, not future evidence): "
        "Your three ideas may be elaborate restatements of existing price path, "
        "risk-calibration, and model consensus. Critically distinguish SIGNED "
        "incremental information from improved VOLATILITY LABEL scaling. "
        "Attack point-in-time availability, overnight maintenance, inability "
        "to know after-17US macro outcomes, drift after 2025, 2026 already "
        "inspected selection risk, correlated model recommendations, severe "
        "DOWN recall and insufficient venue coverage. "
        "Choose ONE cheapest genuinely novel, empirically falsifiable signal "
        "that can be tested with **already evidenced source features**. "
        "If none is credible, state that explicitly and define the minimum "
        "new raw source/time-stamped dataset required. "
        "Give a precise minimum experiment plan and explicit failure criterion; "
        "do NOT invent a 2026 performance figure or pass condition."
    )
    second, usage2 = _generate(
        key, model,
        [
            {"role": "user", "parts": [{"text": initial}]},
            {"role": "model", "parts": [{"text": first}]},
            {"role": "user", "parts": [{"text": challenge}]},
        ],
        3100,
    )
    # Gemini text stays data. There is NO code execution, scraping, or tooling.
    output = (
        "# Gemini independent peer review — external-safe 09TR/17TR XAU research\n\n"
        "This is **unverified Gemini generated research** and must not be "
        "treated as confirmed empirical results, literature, trading advice, "
        "or executable model designs. Human/assistant review is required.\n\n"
        f"Model: {model}\n\n"
        f"External-safe brief SHA256: `{digest}`\n\n"
        "## Round 1 — Independent hypotheses\n\n"
        + first + "\n\n"
        "## Round 2 — Critical challenge and revised priority\n\n"
        + second + "\n"
    )
    Path(str(STEM) + "_REVIEW.md").write_text(output, encoding="utf-8")
    receipt = {
        "status": "GEMINI_TWO_ROUND_INDEPENDENT_RESEARCH_COMPLETED",
        "model": model,
        "run_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "external_safe_brief_path": BRIEF.name,
        "external_safe_brief_sha256": digest,
        "two_total_generate_calls": 2,
        "round1_tokens": usage1,
        "round2_tokens": usage2,
        "no_private_quotes_source_code_or_credentials_transmitted": True,
        "no_model_code_executed": True,
        "no_forecasting_accuracy_claimed": True,
        "no_automated_trade_or_promotion": True,
        "review_is_unverified_generated_ideas": True,
    }
    Path(str(STEM) + "_RESULT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    fail = Path(str(STEM) + "_FAILURE_QC.json")
    if fail.exists():
        fail.unlink()  # Superseded diagnosis, no longer the final outcome.
    print("GEMINI_TWO_ROUND_RESEARCH: PASS")
    print("GEMINI_ROUND1_CHARACTERS:", len(first))
    print("GEMINI_ROUND2_CHARACTERS:", len(second))
    print("GEMINI_RESEARCH_RESULT:", receipt["status"])

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # No network or response body printed. Never include HTTP response detail,
        # prompt, full trace, or environmental values in public logs.
        allowed = str(exc)
        if not (
            allowed.startswith(("GEMINI_", "EXTERNAL_SAFE_", "NO_APPROVED_", "OUTPUT_TOKEN_CAP"))
        ):
            allowed = type(exc).__name__ + "_UNEXPECTED_RUN_FAILURE"
        out = {
            "status": "GEMINI_CONNECTOR_FAIL_CLOSED",
            "safe_reason": allowed[:130],
            "no_claim_of_success": True,
            "no_secret_values_written": True,
        }
        Path(str(STEM) + "_FAILURE_QC.json").write_text(
            json.dumps(out, indent=2) + "\n", encoding="utf-8"
        )
        print("GEMINI_CONNECTOR_STATUS:", out["status"], out["safe_reason"])
        raise SystemExit(1)
