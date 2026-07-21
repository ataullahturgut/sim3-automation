from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
from typing import Any

VERSION = "4.5.0-git-enabled-with-explicit-authorization"
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{3,160}$")
REPORT_RE = re.compile(r"^[A-Za-z0-9_.-]+_FULL\.txt$")


class RunnerError(RuntimeError):
    pass


def utc_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.gmtime())


PERCENT_ENV_RE = re.compile(r"%([^%]+)%")


def _expand_percent_environment(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return os.environ.get(name, match.group(0))

    return PERCENT_ENV_RE.sub(replace, value)


def expand_path(value: str) -> Path:
    expanded = _expand_percent_environment(value)
    expanded = os.path.expandvars(os.path.expanduser(expanded))
    return Path(expanded).resolve()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp, path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RunnerError(f"CONFIG_NOT_FOUND:{path}") from exc
    except json.JSONDecodeError as exc:
        raise RunnerError(f"CONFIG_JSON_INVALID:{exc}") from exc
    if not isinstance(data, dict):
        raise RunnerError("CONFIG_ROOT_MUST_BE_OBJECT")
    return data


def marker(text: str, name: str) -> str:
    prefix = f"# {name}="
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def derive_task_id(task_path: Path, text: str) -> str:
    declared = marker(text, "TASK_ID")
    if declared:
        if not TASK_ID_RE.fullmatch(declared):
            raise RunnerError(f"TASK_ID_INVALID:{declared}")
        return declared
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", task_path.stem).strip("_.-")
    if len(stem) < 3:
        stem = "SIM3_TASK"
    return f"{stem}_{utc_stamp()}"


def determine_mode(text: str, default_mode: str) -> tuple[str, str]:
    mode = marker(text, "MODE") or default_mode
    if mode == "CODEX_READ_ONLY":
        return mode, "read-only"
    if mode == "CODEX_WORKSPACE_WRITE":
        return mode, "workspace-write"
    raise RunnerError(f"MODE_NOT_SUPPORTED:{mode}")


def determine_timeout_seconds(task_text: str, mode: str, config: dict[str, Any]) -> tuple[int, str]:
    declared = marker(task_text, "HARD_TIMEOUT_SECONDS")
    if declared:
        try:
            value = int(declared)
        except ValueError as exc:
            raise RunnerError(f"HARD_TIMEOUT_SECONDS_INVALID:{declared}") from exc
        if value < 60 or value > 1800:
            raise RunnerError(f"HARD_TIMEOUT_SECONDS_OUT_OF_RANGE:{value}")
        return value, "TASK_MARKER"

    default_value = 600 if mode == "CODEX_READ_ONLY" else 900
    configured = int(config.get("timeout_seconds", default_value))
    value = min(max(60, configured), default_value)
    return value, "MODE_DEFAULT_CAPPED_BY_CONFIG"


def terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
            check=False,
        )
    else:
        process.kill()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def determine_report_name(text: str, task_id: str) -> str:
    name = marker(text, "REPORT_FILENAME") or f"{task_id}_FULL.txt"
    if Path(name).name != name or not REPORT_RE.fullmatch(name):
        raise RunnerError(f"REPORT_FILENAME_INVALID:{name}")
    return name


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


class SingleRunnerLock:
    def __init__(self, path: Path):
        self.path = path
        self.acquired = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            existing_pid = 0
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                existing_pid = int(data.get("pid", 0))
            except Exception:
                existing_pid = 0
            if pid_alive(existing_pid):
                raise RunnerError(f"RUNNER_ALREADY_ACTIVE_PID:{existing_pid}")
            self.path.unlink(missing_ok=True)

        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(self.path, flags)
        except FileExistsError as exc:
            raise RunnerError("RUNNER_LOCK_ACQUIRE_RACE") from exc
        try:
            payload = json.dumps({"pid": os.getpid(), "acquired_at": utc_stamp()}) + "\n"
            os.write(fd, payload.encode("utf-8"))
        finally:
            os.close(fd)
        self.acquired = True

    def release(self) -> None:
        if self.acquired:
            self.path.unlink(missing_ok=True)
            self.acquired = False

    def __enter__(self) -> "SingleRunnerLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


def build_contract(mode: str) -> str:
    if mode == "CODEX_READ_ONLY":
        git_rule = "Do not use Git commands."
        mode_rules = [
            "Do not modify, create, delete, rename or move workspace files.",
            "This is a non-interactive read-only run.",
            "You may use the available shell tool only for repository-local read-only inspection.",
            "Allowed read-only purposes are file existence checks, directory listing, text search and file content reading.",
            "Use the narrowest possible command and remain inside the configured repository.",
            "Do not run tests, imports, compilers, application entrypoints, package installers or generated scripts.",
            "Do not access a database, network service or external system.",
            "If a needed fact cannot be proven with read-only inspection, report it as UNKNOWN.",
        ]
    else:
        git_rule = "Git status, diff, add, commit, push and remote verification are allowed only when the original task explicitly authorizes them. Git reset, restore, checkout, clean, stash, branch creation/deletion and recovery flows remain forbidden unless the original task explicitly authorizes them."
        mode_rules = [
            "Workspace source changes are allowed only when the task explicitly asks for them.",
            "When commands are needed, run the narrowest direct command and avoid nested PowerShell or cmd wrappers.",
            "Do not discard existing user changes.",
        ]
    return "\n".join(
        [
            "",
            "SIM3_V4_5_WORKER_CONTRACT_BEGIN",
            "Use one agent only. Do not spawn subagents.",
            git_rule,
            *mode_rules,
            "Do not start the application or NiceGUI.",
            "Do not access a real database or network unless the original task explicitly authorizes it.",
            "Do not write the automation report file yourself. Return the complete result in your final answer; the Worker owns report creation.",
            "Be evidence-based. State unknowns honestly.",
            "SIM3_V4_5_WORKER_CONTRACT_END",
            "",
        ]
    )


def find_codex() -> str:
    override = os.environ.get("SIM3_V3_CODEX_EXE", "").strip()
    if override:
        p = expand_path(override)
        if not p.is_file():
            raise RunnerError(f"CODEX_OVERRIDE_NOT_FOUND:{p}")
        return str(p)
    found = shutil.which("codex") or shutil.which("codex.exe")
    if not found:
        raise RunnerError("CODEX_NOT_FOUND_IN_PATH")
    return found


def extract_reported_final_status(final_text: str) -> str:
    matches = re.findall(
        r"(?mi)^FINAL_STATUS\s*=\s*([A-Za-z0-9_.-]+)\s*$",
        final_text,
    )
    return matches[-1].upper() if matches else ""


def classify_reported_final_status(reported: str) -> tuple[str, str, list[str]]:
    if not reported:
        return "", "NONE", []

    failure_statuses = {
        "FAILED",
        "BLOCKED",
        "ERROR",
        "VALIDATION_FAILED",
        "TEST_IMPLEMENTED_BUT_VALIDATION_FAILED",
    }
    warning_statuses = {
        "PARTIAL",
        "PARTIAL_EVIDENCE",
        "OK_WITH_WARNINGS",
    }
    success_statuses = {
        "OK",
        "PASS",
        "SUCCESS",
        "COMPLETED",
    }

    if reported in failure_statuses:
        return "FAILED", f"CODEX_REPORTED_{reported}", []

    if reported in warning_statuses:
        return "OK_WITH_WARNINGS", "NONE", [f"CODEX_REPORTED_{reported}"]

    if reported in success_statuses:
        return "OK", "NONE", []

    return "OK_WITH_WARNINGS", "NONE", [f"CODEX_REPORTED_UNMAPPED_STATUS_{reported}"]


def prepare_process_command(codex_args: list[str]) -> tuple[list[str], str]:
    executable = Path(codex_args[0])
    if os.name == "nt" and executable.suffix.lower() in {".cmd", ".bat"}:
        comspec = os.environ.get("ComSpec", "").strip() or shutil.which("cmd.exe")
        if not comspec:
            raise RunnerError("WINDOWS_COMMAND_PROCESSOR_NOT_FOUND")
        # Windows cannot CreateProcess an npm .cmd launcher directly. Invoke the batch
        # file through cmd.exe with CALL, but keep the task body on stdin. Do not wrap
        # the complete command in an extra quote pair: cmd.exe would treat the leading
        # escaped quote as part of the executable name (the V3.0 failure).
        command_text = "call " + subprocess.list2cmdline(codex_args)
        return [comspec, "/d", "/s", "/c", command_text], "WINDOWS_CMD_CALL_SHIM"
    return codex_args, "DIRECT_EXECUTABLE"


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    config_path = root / "CONFIG" / "sim3_v3_config.json"
    config = read_json(config_path)

    task_path = Path(args.task).resolve()
    if not task_path.is_file():
        raise RunnerError(f"TASK_FILE_NOT_FOUND:{task_path}")
    task_text = task_path.read_text(encoding="utf-8-sig")
    if not task_text.strip():
        raise RunnerError("TASK_FILE_EMPTY")

    repo_value = os.environ.get("SIM3_V3_REPO", str(config.get("repo", ""))).strip()
    if not repo_value:
        raise RunnerError("REPOSITORY_PATH_EMPTY")
    repo = expand_path(repo_value)
    if not repo.is_dir():
        raise RunnerError(f"REPOSITORY_NOT_FOUND:{repo}")

    task_id = derive_task_id(task_path, task_text)
    mode, sandbox = determine_mode(task_text, str(config.get("default_mode", "CODEX_READ_ONLY")))
    report_name = determine_report_name(task_text, task_id)
    reasoning = str(config.get("reasoning_effort", "medium"))
    verbosity = str(config.get("model_verbosity", "low"))
    approval = str(config.get("approval_policy", "never"))
    if approval not in {"untrusted", "on-request", "never"}:
        raise RunnerError(f"APPROVAL_POLICY_INVALID:{approval}")
    ignore_rules = bool(config.get("ignore_execpolicy_rules", True))
    timeout_seconds, timeout_source = determine_timeout_seconds(task_text, mode, config)

    run_id = f"{utc_stamp()}_{task_id}_{uuid.uuid4().hex[:8]}"
    run_dir = root / "RUNTIME" / run_id
    reports_dir = root / "REPORTS"
    report_path = reports_dir / report_name
    ready_path = reports_dir / f"{task_id}.ready.json"
    events_path = run_dir / "codex_events.jsonl"
    stderr_path = run_dir / "codex_stderr.txt"
    final_path = run_dir / "codex_final_message.txt"
    exact_task_path = run_dir / "task_exact_utf8.txt"
    metadata_path = run_dir / "run_metadata.json"

    prompt_text = task_text.rstrip() + "\n" + build_contract(mode)
    task_sha = hashlib.sha256(task_text.encode("utf-8")).hexdigest()

    codex_exe = find_codex()
    codex_found = True

    cmd = [
        codex_exe,
        "--ask-for-approval", approval,
        "--sandbox", sandbox,
        "--config", f"model_reasoning_effort={reasoning}",
        "--config", f"model_verbosity={verbosity}",
        "exec",
    ]
    if ignore_rules:
        cmd.append("--ignore-rules")
    cmd += [
        "--cd", str(repo),
        "--ephemeral",
        "--json",
        "--output-last-message", str(final_path),
        "-",
    ]

    process_cmd, launch_method = prepare_process_command(cmd)

    metadata = {
        "version": VERSION,
        "run_id": run_id,
        "task_id": task_id,
        "task_file": str(task_path),
        "task_sha256": task_sha,
        "mode": mode,
        "sandbox": sandbox,
        "approval_policy": approval,
        "ignore_execpolicy_rules": ignore_rules,
        "repo": str(repo),
        "report_path": str(report_path),
        "codex_command": cmd,
        "process_command": process_cmd,
        "launch_method": launch_method,
        "codex_executable_found": codex_found,
        "timeout_seconds": timeout_seconds,
        "timeout_source": timeout_source,
        "status": "VALIDATED_ONLY" if args.validate_only else "STARTING",
    }

    if args.validate_only:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return 0

    lock_path = root / "RUNTIME" / "SIM3_V3_RUNNER.lock"
    with SingleRunnerLock(lock_path):
        run_dir.mkdir(parents=True, exist_ok=False)
        atomic_write_text(exact_task_path, task_text)
        atomic_write_json(metadata_path, metadata)

        started = time.time()
        return_code = -1
        failure_reason = "NONE"
        timed_out = False

        with events_path.open("wb") as events, stderr_path.open("wb") as stderr:
            process: subprocess.Popen[bytes] | None = None
            try:
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                process = subprocess.Popen(
                    process_cmd,
                    stdin=subprocess.PIPE,
                    stdout=events,
                    stderr=stderr,
                    cwd=str(repo),
                    shell=False,
                    creationflags=creationflags,
                )
                process.communicate(input=prompt_text.encode("utf-8"), timeout=timeout_seconds)
                return_code = int(process.returncode or 0)
            except subprocess.TimeoutExpired:
                timed_out = True
                failure_reason = f"CODEX_TIMEOUT_{timeout_seconds}_SECONDS"
                if process is not None:
                    terminate_process_tree(process)
            except OSError as exc:
                failure_reason = f"CODEX_START_FAILED:{exc}"
                if process is not None:
                    terminate_process_tree(process)

        duration = round(time.time() - started, 3)
        final_text = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.is_file() else ""

        policy_block_count = len(re.findall(r"blocked by policy", stderr_text, flags=re.IGNORECASE))
        warning_reasons: list[str] = []
        if policy_block_count:
            warning_reasons.append("CODEX_COMMAND_BLOCKED_BY_POLICY")

        reported_final_status = extract_reported_final_status(final_text)
        reported_worker_status, reported_failure_reason, reported_warnings = (
            classify_reported_final_status(reported_final_status)
        )
        warning_reasons.extend(reported_warnings)

        if timed_out:
            status = "FAILED"
        elif return_code != 0:
            status = "FAILED"
            if failure_reason == "NONE":
                failure_reason = f"CODEX_RETURN_CODE_{return_code}"
        elif not final_text.strip():
            status = "FAILED"
            failure_reason = "CODEX_FINAL_MESSAGE_MISSING_OR_EMPTY"
        elif reported_worker_status == "FAILED":
            status = "FAILED"
            failure_reason = reported_failure_reason
        elif reported_worker_status == "OK_WITH_WARNINGS":
            status = "OK_WITH_WARNINGS"
        else:
            status = "OK_WITH_WARNINGS" if warning_reasons else "OK"

        report_lines = [
            "STEP=SIM3_V3_DIRECT_TASK_RUNNER",
            f"VERSION={VERSION}",
            f"RUN_ID={run_id}",
            f"TASK_ID={task_id}",
            f"TASK_SHA256={task_sha}",
            f"MODE={mode}",
            f"SANDBOX={sandbox}",
            f"APPROVAL_POLICY={approval}",
            f"EXEC_POLICY_RULE_FILES_IGNORED={str(ignore_rules)}",
            f"LAUNCH_METHOD={launch_method}",
            f"REPOSITORY={repo}",
            f"TASK_FILE={task_path}",
            f"EXACT_TASK_COPY={exact_task_path}",
            f"CODEX_EVENTS={events_path}",
            f"CODEX_STDERR={stderr_path}",
            f"CODEX_FINAL_MESSAGE_PATH={final_path}",
            f"CODEX_RETURN_CODE={return_code}",
            f"HARD_TIMEOUT_SECONDS={timeout_seconds}",
            f"HARD_TIMEOUT_SOURCE={timeout_source}",
            f"TIMED_OUT={str(timed_out)}",
            f"DURATION_SECONDS={duration}",
            f"FAILURE_REASON={failure_reason}",
            f"CODEX_REPORTED_FINAL_STATUS={reported_final_status or 'NOT_FOUND'}",
            f"POLICY_BLOCK_COUNT={policy_block_count}",
            f"WARNING_COUNT={len(warning_reasons)}",
            f"WARNING_REASONS={','.join(warning_reasons) if warning_reasons else 'NONE'}",
            "",
            "===== CODEX_FINAL_MESSAGE =====",
            final_text.rstrip(),
            "",
            "===== CODEX_STDERR =====",
            stderr_text.rstrip(),
            "",
            f"FAILURE_COUNT={0 if status in {'OK', 'OK_WITH_WARNINGS'} else 1}",
            f"FINAL_STATUS={status}",
            "",
        ]
        atomic_write_text(report_path, "\n".join(report_lines))

        ready = {
            "version": VERSION,
            "run_id": run_id,
            "task_id": task_id,
            "task_sha256": task_sha,
            "report_filename": report_name,
            "report_path": str(report_path),
            "codex_return_code": return_code,
            "failure_reason": failure_reason,
            "codex_reported_final_status": reported_final_status or "NOT_FOUND",
            "final_status": status,
            "policy_block_count": policy_block_count,
            "warning_count": len(warning_reasons),
            "warning_reasons": warning_reasons,
            "worker_report_ready": True,
        }
        atomic_write_json(ready_path, ready)
        atomic_write_json(reports_dir / "LATEST_READY.json", ready)

        print(f"RUN_ID={run_id}")
        print(f"REPORT_PATH={report_path}")
        print(f"READY_PATH={ready_path}")
        print(f"FINAL_STATUS={status}")
        return 0 if status in {"OK", "OK_WITH_WARNINGS"} else 1



def main() -> int:
    parser = argparse.ArgumentParser(description="SIM3 V3 direct Codex task runner")
    parser.add_argument("--root", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        return run(args)
    except RunnerError as exc:
        print(f"SIM3_V3_ERROR={exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"SIM3_V3_UNEXPECTED_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
