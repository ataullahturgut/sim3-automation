from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def read_key_value(path: Path, key: str) -> str:
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    prefix = key + "="
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}.{int(time.time() * 1000)}")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    last_error: Exception | None = None
    for _ in range(40):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.1)
    try:
        fallback = path.with_name(path.name + f".write_failed.{os.getpid()}.{int(time.time() * 1000)}")
        os.replace(tmp, fallback)
    except Exception:
        pass
    if last_error is not None:
        raise last_error


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def normalize_path(value: str | Path) -> str:
    try:
        return os.path.normcase(os.path.abspath(os.fspath(value)))
    except Exception:
        return os.fspath(value).strip().lower()


def same_path(left: str | Path, right: str | Path) -> bool:
    return normalize_path(left) == normalize_path(right)


class LoopController:
    def __init__(self, root: Path, max_loops: int, mode: str) -> None:
        self.root = root
        self.max_loops = max_loops
        self.mode = mode
        self.started_at = now_stamp()
        self.start_time = time.time()
        self.loop_dir = root / "LOOP"
        self.result_path = self.loop_dir / "LAST_LOOP_RESULT.txt"
        self.history_path = self.loop_dir / "LOOP_HISTORY.txt"
        self.diagnostic_path = self.loop_dir / "LAST_AUTOMATION_STOP_DIAGNOSTIC.txt"
        self.pending_delivery_path = self.loop_dir / "PENDING_DELIVERY.json"
        self.state = "INITIALIZING"
        self.current_loop = 0
        self.capture_status = ""
        self.capture_run_token = ""
        self.delivery_status = ""
        self.delivery_run_token = ""
        self.delivery_attempt = 0
        self.response_status = ""
        self.response_run_token = ""
        self.response_attempt = 0
        self.failure_reason = "NONE"
        self.last_report = ""
        self.stop_after_current = False
        self.loop_dir.mkdir(parents=True, exist_ok=True)
        self.worker_timeout_seconds = self.read_worker_timeout_seconds()
        self.capture_timeout_seconds = max(900, self.worker_timeout_seconds + 420)
        self.delivery_timeout_seconds = 300
        self.response_timeout_seconds = 780
        self.inter_loop_settle_seconds = 3
        self.delivery_retry_limit = 3
        self.response_retry_limit = 2

    def read_worker_timeout_seconds(self) -> int:
        config_path = self.root / "CONFIG" / "sim3_v3_config.json"
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return max(60, int(data.get("timeout_seconds", 1800)))
        except Exception:
            return 1800

    @staticmethod
    def read_tail(path: Path, max_chars: int = 24000) -> str:
        if not path.is_file():
            return "FILE_NOT_FOUND"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return f"READ_FAILED:{type(exc).__name__}:{exc}"
        if len(text) > max_chars:
            return "[TRUNCATED_TO_LAST_CHARS]\n" + text[-max_chars:]
        return text

    def append_history(self, message: str) -> None:
        self.loop_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"{now_stamp()} LOOP={self.current_loop} {message}\n")

    def write_status(self, final_status: str, reason: str) -> None:
        elapsed = int(time.time() - self.start_time)
        text = "\n".join(
            [
                "STEP=SIM3_V4_7_UNIFIED_LOOP_CONTROLLER",
                f"STARTED_AT={self.started_at}",
                f"UPDATED_AT={now_stamp()}",
                f"ELAPSED_SECONDS={elapsed}",
                f"ROOT={self.root}",
                f"MODE={self.mode}",
                f"MAX_LOOPS={self.max_loops}",
                f"CURRENT_LOOP={self.current_loop}",
                f"LAST_STATE={self.state}",
                f"CAPTURE_STATUS={self.capture_status}",
                f"CAPTURE_RUN_TOKEN={self.capture_run_token}",
                f"DELIVERY_STATUS={self.delivery_status}",
                f"DELIVERY_RUN_TOKEN={self.delivery_run_token}",
                f"DELIVERY_ATTEMPT={self.delivery_attempt}",
                f"RESPONSE_STATUS={self.response_status}",
                f"RESPONSE_RUN_TOKEN={self.response_run_token}",
                f"RESPONSE_ATTEMPT={self.response_attempt}",
                f"LAST_REPORT={self.last_report}",
                f"PENDING_DELIVERY_PRESENT={self.pending_delivery_path.is_file()}",
                f"WORKER_TIMEOUT_SECONDS={self.worker_timeout_seconds}",
                f"CAPTURE_TIMEOUT_SECONDS={self.capture_timeout_seconds}",
                f"DELIVERY_TIMEOUT_SECONDS={self.delivery_timeout_seconds}",
                f"RESPONSE_TIMEOUT_SECONDS={self.response_timeout_seconds}",
                f"INTER_LOOP_SETTLE_SECONDS={self.inter_loop_settle_seconds}",
                f"RESULT_REASON={reason}",
                f"FINAL_STATUS={final_status}",
                "",
            ]
        )
        atomic_write(self.result_path, text)

    def latest_runtime_dir(self) -> Path | None:
        runtime_root = self.root / "RUNTIME"
        if not runtime_root.is_dir():
            return None
        try:
            dirs = [item for item in runtime_root.iterdir() if item.is_dir()]
            return max(dirs, key=lambda item: item.stat().st_mtime) if dirs else None
        except Exception:
            return None

    def relevant_processes(self) -> str:
        if os.name != "nt":
            return "PROCESS_LIST_NOT_WINDOWS"
        try:
            result = subprocess.run(
                ["tasklist.exe", "/fo", "csv", "/nh"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                errors="replace",
                timeout=15,
                check=False,
            )
            keywords = ("codex", "python", "cmd.exe", "powershell", "autohotkey")
            lines = [line for line in result.stdout.splitlines() if any(key in line.lower() for key in keywords)]
            return "\n".join(lines) if lines else "NO_RELEVANT_PROCESS_FOUND"
        except Exception as exc:
            return f"PROCESS_LIST_FAILED:{type(exc).__name__}:{exc}"

    def write_stop_diagnostic(self, reason: str) -> None:
        latest_runtime = self.latest_runtime_dir()
        parts = [
            "STEP=SIM3_V4_7_AUTOMATION_STOP_DIAGNOSTIC",
            f"CREATED_AT={now_stamp()}",
            f"ROOT={self.root}",
            f"CURRENT_LOOP={self.current_loop}",
            f"LAST_STATE={self.state}",
            f"FAILURE_REASON={reason}",
            f"CAPTURE_STATUS={self.capture_status}",
            f"CAPTURE_RUN_TOKEN={self.capture_run_token}",
            f"DELIVERY_STATUS={self.delivery_status}",
            f"DELIVERY_RUN_TOKEN={self.delivery_run_token}",
            f"DELIVERY_ATTEMPT={self.delivery_attempt}",
            f"RESPONSE_STATUS={self.response_status}",
            f"RESPONSE_RUN_TOKEN={self.response_run_token}",
            f"RESPONSE_ATTEMPT={self.response_attempt}",
            f"LAST_REPORT={self.last_report}",
            f"PENDING_DELIVERY={self.pending_delivery_path if self.pending_delivery_path.is_file() else 'NONE'}",
            f"STOP_FLAG_PRESENT={(self.root / 'STOP.flag').exists()}",
            f"PAUSE_FLAG_PRESENT={(self.root / 'PAUSE.flag').exists()}",
            f"LATEST_RUNTIME={latest_runtime or 'NOT_FOUND'}",
            "",
        ]
        evidence_files = [
            ("CAPTURE_RESULT", self.root / "CAPTURE" / "LAST_CAPTURE_RESULT.txt"),
            ("DELIVERY_RESULT", self.root / "DELIVERY" / "LAST_DELIVERY_RESULT.txt"),
            ("RESPONSE_RESULT", self.root / "RESPONSE" / "LAST_RESPONSE_WAIT_RESULT.txt"),
            ("LOOP_CONSOLE", self.loop_dir / "LAST_LOOP_CONSOLE.txt"),
            ("LOOP_HISTORY", self.history_path),
            ("PENDING_DELIVERY", self.pending_delivery_path),
        ]
        for label, path in evidence_files:
            parts.extend([f"===== {label}: {path} =====", self.read_tail(path), ""])
        if latest_runtime is not None:
            for label, filename, limit in [
                ("RUN_METADATA", "run_metadata.json", 16000),
                ("CODEX_STDERR", "codex_stderr.txt", 24000),
                ("CODEX_FINAL_MESSAGE", "codex_final_message.txt", 32000),
            ]:
                path = latest_runtime / filename
                parts.extend([f"===== {label}: {path} =====", self.read_tail(path, limit), ""])
        parts.extend(["===== RELEVANT_PROCESSES =====", self.relevant_processes(), "", "FINAL_STATUS=AUTOMATION_STOP_DIAGNOSTIC_READY", ""])
        try:
            atomic_write(self.diagnostic_path, "\n".join(parts))
        except Exception:
            pass
        # Deliberately do not open Notepad here. A diagnostic window can steal
        # browser/file-dialog focus and make the next retry less reliable.

    def run_cmd(self, cmd_name: str) -> int:
        cmd = self.root / cmd_name
        if not cmd.is_file():
            self.failure_reason = f"CMD_NOT_FOUND:{cmd_name}"
            return 901
        self.append_history(f"START_CMD={cmd_name}")
        proc = subprocess.Popen(["cmd.exe", "/d", "/s", "/c", str(cmd)], cwd=str(self.root), creationflags=0)
        rc = proc.wait()
        self.append_history(f"END_CMD={cmd_name} RC={rc}")
        return rc

    def start_cmd(self, cmd_name: str) -> int:
        cmd = self.root / cmd_name
        if not cmd.is_file():
            self.failure_reason = f"CMD_NOT_FOUND:{cmd_name}"
            return 901
        self.append_history(f"START_ASYNC_CMD={cmd_name}")
        proc = subprocess.Popen(["cmd.exe", "/d", "/s", "/c", str(cmd)], cwd=str(self.root), creationflags=0)
        try:
            rc = proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            rc = 0
        self.append_history(f"ASYNC_CMD_TRIGGERED={cmd_name} RC={rc}")
        return rc

    def delete_if_exists(self, relative: str) -> None:
        path = self.root / relative
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass

    def find_latest_report(self) -> str:
        reports_dir = self.root / "REPORTS"
        ready_path = reports_dir / "LATEST_READY.json"
        try:
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            candidate = Path(str(ready.get("report_path", "")))
            if candidate.is_file() and candidate.name.endswith("_FULL.txt") and candidate.stat().st_size > 0:
                return str(candidate)
        except Exception:
            pass
        try:
            candidates = [p for p in reports_dir.glob("*_FULL.txt") if p.is_file() and p.stat().st_size > 0]
            return str(max(candidates, key=lambda p: p.stat().st_mtime)) if candidates else ""
        except Exception:
            return ""

    def report_from_capture_result(self) -> str:
        result = self.root / "CAPTURE" / "LAST_CAPTURE_RESULT.txt"
        candidate = read_key_value(result, "REPORT_PATH")
        if candidate:
            path = Path(candidate)
            if path.is_file() and path.name.endswith("_FULL.txt") and path.stat().st_size > 0:
                return str(path)
        return self.find_latest_report()

    def save_pending_delivery(self, report: str, reason: str, phase: str = "WAITING_DELIVERY") -> None:
        path = Path(report)
        atomic_write_json(
            self.pending_delivery_path,
            {
                "report_path": str(path),
                "report_name": path.name,
                "report_size": path.stat().st_size if path.is_file() else -1,
                "created_at": now_stamp(),
                "phase": phase,
                "reason": reason,
            },
        )

    def clear_pending_delivery(self) -> None:
        try:
            if self.pending_delivery_path.exists():
                self.pending_delivery_path.unlink()
        except Exception:
            pass

    def load_pending_delivery(self) -> tuple[str, str]:
        if self.pending_delivery_path.is_file():
            try:
                data = json.loads(self.pending_delivery_path.read_text(encoding="utf-8"))
                candidate = Path(str(data.get("report_path", "")))
                phase = str(data.get("phase", "WAITING_DELIVERY")).strip().upper() or "WAITING_DELIVERY"
                if phase not in {"WAITING_DELIVERY", "WAITING_RESPONSE"}:
                    phase = "WAITING_DELIVERY"
                if candidate.is_file() and candidate.name.endswith("_FULL.txt") and candidate.stat().st_size > 0:
                    return str(candidate), phase
            except Exception:
                pass
        # Migration path for installations that failed before this unified patch:
        # infer a resumable report from the last delivery result.
        delivery_result = self.root / "DELIVERY" / "LAST_DELIVERY_RESULT.txt"
        status = read_key_value(delivery_result, "FINAL_STATUS")
        source = read_key_value(delivery_result, "SOURCE_REPORT")
        if status in {"FAILED", "PAUSED", "STARTING", "UPLOADING", "ATTACHED"} and source:
            candidate = Path(source)
            if candidate.is_file() and candidate.name.endswith("_FULL.txt") and candidate.stat().st_size > 0:
                self.save_pending_delivery(
                    str(candidate),
                    f"INFERRED_FROM_LAST_DELIVERY_{status}",
                    phase="WAITING_DELIVERY",
                )
                return str(candidate), "WAITING_DELIVERY"
        return "", ""

    def wait_stage_result(
        self,
        rel_path: str,
        stage: str,
        timeout_seconds: int,
        expected_token: str,
        ok_values: set[str] | None = None,
    ) -> tuple[bool, str, str]:
        ok_values = ok_values or {"OK"}
        path = self.root / rel_path
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            value = read_key_value(path, "FINAL_STATUS")
            token = read_key_value(path, "RUN_TOKEN")
            if expected_token and token != expected_token:
                self.state = f"WAIT_{stage.upper()}_STALE_OR_MISSING_TOKEN"
                self.write_status("RUNNING", self.state)
                time.sleep(0.75)
                continue
            if stage == "delivery":
                self.delivery_status = value
            elif stage == "response":
                self.response_status = value
            self.state = f"WAIT_{stage.upper()}_{value or 'NO_STATUS'}"
            self.write_status("RUNNING", self.state)
            if value in ok_values:
                return True, value, read_key_value(path, "RESULT_REASON")
            if value in {"FAILED", "PAUSED"}:
                reason = read_key_value(path, "RESULT_REASON")
                if stage == "response" and value == "PAUSED" and reason == "RESPONSE_COMPLETE_NOT_CONFIRMED_BEFORE_TIMEOUT":
                    try:
                        stable = int(read_key_value(path, "STABLE_COMPLETE_COUNT") or "0")
                    except ValueError:
                        stable = 0
                    evidence = read_key_value(path, "COMPLETION_EVIDENCE")
                    if stable >= 2 and evidence in {"COPY_ICON_VISIBLE_STOP_ABSENT", "ACTION_PAIR_VISIBLE_STOP_ABSENT"}:
                        self.response_status = "OK_RECOVERED_FROM_CONTRADICTORY_WRITER_STATE"
                        self.append_history(f"RESPONSE_FALSE_NEGATIVE_RECOVERED TOKEN={expected_token} STABLE={stable} EVIDENCE={evidence}")
                        return True, self.response_status, reason
                return False, value, reason
            time.sleep(1.0)
        return False, "TIMEOUT", f"{stage.upper()}_TIMEOUT"

    def wait_capture_done(self, expected_token: str) -> bool:
        path = self.root / "CAPTURE" / "LAST_CAPTURE_RESULT.txt"
        deadline = time.monotonic() + self.capture_timeout_seconds
        while time.monotonic() < deadline:
            value = read_key_value(path, "FINAL_STATUS")
            reason = read_key_value(path, "RESULT_REASON")
            token = read_key_value(path, "RUN_TOKEN")
            if token != expected_token:
                self.state = "WAIT_CAPTURE_STALE_OR_MISSING_TOKEN"
                self.write_status("RUNNING", self.state)
                time.sleep(0.75)
                continue
            self.capture_status = value
            self.state = f"WAIT_CAPTURE_{value or 'NO_STATUS'}"
            self.write_status("RUNNING", self.state)
            if value == "OK":
                return True
            if value == "NO_NEXT_COMMAND":
                self.stop_after_current = True
                self.state = "NO_NEXT_COMMAND_TERMINAL_RESPONSE"
                return True
            if value in {"FAILED", "PAUSED"}:
                latest = self.report_from_capture_result()
                if latest and reason.startswith("RUNNER_EXIT_CODE_"):
                    self.capture_status = f"{value}_REPORT_AVAILABLE"
                    self.last_report = latest
                    self.append_history(f"CAPTURE_{value}_BUT_REPORT_AVAILABLE REASON={reason}")
                    return True
                self.failure_reason = f"CAPTURE_{value}:{reason}"
                return False
            time.sleep(1.0)
        self.failure_reason = "CAPTURE_TIMEOUT"
        return False

    @staticmethod
    def delivery_failure_retryable(reason: str) -> bool:
        # Retry only failures known to occur before a file is attached or sent.
        # This prevents duplicate attachments/messages after an uncertain late-stage
        # UI failure. Persistent failures remain in PENDING_DELIVERY for safe resume.
        retryable_prefixes = (
            "DELIVERY_START_RC_",
            "CHATGPT_BROWSER_WINDOW_NOT_FOUND",
            "BROWSER_ACTIVATION_FAILED",
            "ATTACH_BUTTON_NOT_FOUND",
            "FILE_DIALOG_NOT_OPENED",
            "FILE_DIALOG_PATH_SET_FAILED",
        )
        return reason.startswith(retryable_prefixes)

    def deliver_report_with_retry(self, report: str) -> bool:
        self.last_report = report
        self.save_pending_delivery(report, "WAITING_DELIVERY", phase="WAITING_DELIVERY")
        for attempt in range(1, self.delivery_retry_limit + 1):
            self.delivery_attempt = attempt
            self.delivery_run_token = f"{now_stamp()}_LOOP_{self.current_loop}_DELIVERY_{attempt}_PID_{os.getpid()}"
            atomic_write(self.root / "DELIVERY" / "CURRENT_DELIVERY_TOKEN.txt", self.delivery_run_token + "\n")
            atomic_write(self.root / "DELIVERY" / "CURRENT_DELIVERY_REPORT.txt", report + "\n")
            self.delete_if_exists("DELIVERY/LAST_DELIVERY_RESULT.txt")
            self.append_history(f"DELIVERY_ATTEMPT_START ATTEMPT={attempt} TOKEN={self.delivery_run_token} REPORT={report}")
            rc = self.start_cmd("SIM3_V4_1_DELIVER_LATEST_REPORT.cmd")
            if rc != 0:
                reason = f"DELIVERY_START_RC_{rc}"
                ok = False
                status = "FAILED"
            else:
                ok, status, reason = self.wait_stage_result(
                    "DELIVERY/LAST_DELIVERY_RESULT.txt",
                    "delivery",
                    self.delivery_timeout_seconds,
                    self.delivery_run_token,
                )
            if ok:
                self.delivery_status = "OK"
                self.save_pending_delivery(
                    report,
                    "DELIVERY_CONFIRMED_WAITING_RESPONSE",
                    phase="WAITING_RESPONSE",
                )
                self.append_history(f"DELIVERY_ATTEMPT_OK ATTEMPT={attempt} TOKEN={self.delivery_run_token}")
                return True
            self.delivery_status = status
            self.append_history(f"DELIVERY_ATTEMPT_FAILED ATTEMPT={attempt} STATUS={status} REASON={reason}")
            self.save_pending_delivery(
                report,
                f"DELIVERY_ATTEMPT_{attempt}_{status}_{reason}",
                phase="WAITING_DELIVERY",
            )
            if not self.delivery_failure_retryable(reason) or attempt >= self.delivery_retry_limit:
                self.failure_reason = f"DELIVERY_{status}:{reason}"
                return False
            self.state = "DELIVERY_RETRY_BACKOFF"
            self.write_status("RUNNING", self.state)
            time.sleep(2.0 * attempt)
        self.failure_reason = "DELIVERY_RETRY_EXHAUSTED"
        return False

    def wait_response_with_retry(self) -> bool:
        for attempt in range(1, self.response_retry_limit + 1):
            self.response_attempt = attempt
            self.response_run_token = f"{now_stamp()}_LOOP_{self.current_loop}_RESPONSE_{attempt}_PID_{os.getpid()}"
            atomic_write(self.root / "RESPONSE" / "CURRENT_RESPONSE_TOKEN.txt", self.response_run_token + "\n")
            self.delete_if_exists("RESPONSE/LAST_RESPONSE_WAIT_RESULT.txt")
            self.append_history(f"RESPONSE_ATTEMPT_START ATTEMPT={attempt} TOKEN={self.response_run_token}")
            rc = self.start_cmd("SIM3_V4_2_START_RESPONSE_WAIT.cmd")
            if rc != 0:
                ok = False
                status = "FAILED"
                reason = f"RESPONSE_START_RC_{rc}"
            else:
                ok, status, reason = self.wait_stage_result(
                    "RESPONSE/LAST_RESPONSE_WAIT_RESULT.txt",
                    "response",
                    self.response_timeout_seconds,
                    self.response_run_token,
                )
            if ok:
                self.append_history(f"RESPONSE_ATTEMPT_OK ATTEMPT={attempt} TOKEN={self.response_run_token}")
                return True
            self.append_history(f"RESPONSE_ATTEMPT_FAILED ATTEMPT={attempt} STATUS={status} REASON={reason}")
            if reason == "USER_EMERGENCY_STOP" or attempt >= self.response_retry_limit:
                self.failure_reason = f"RESPONSE_{status}:{reason}"
                return False
            self.state = "RESPONSE_RETRY_BACKOFF"
            self.write_status("RUNNING", self.state)
            time.sleep(2.0)
        self.failure_reason = "RESPONSE_RETRY_EXHAUSTED"
        return False

    def deliver_and_wait_response(self, report: str) -> bool:
        if not self.deliver_report_with_retry(report):
            return False
        if not self.wait_response_with_retry():
            # Delivery was confirmed. Keep WAITING_RESPONSE so a normal restart
            # resumes response detection without uploading the report twice.
            self.save_pending_delivery(
                report,
                "DELIVERY_CONFIRMED_RESPONSE_NOT_YET_CONFIRMED",
                phase="WAITING_RESPONSE",
            )
            return False
        self.clear_pending_delivery()
        return True

    def capture_and_run_task(self) -> bool:
        self.delete_if_exists("CAPTURE/LAST_CAPTURE_RESULT.txt")
        self.capture_run_token = f"{now_stamp()}_LOOP_{self.current_loop}_CAPTURE_PID_{os.getpid()}"
        atomic_write(self.root / "CAPTURE" / "CURRENT_CAPTURE_TOKEN.txt", self.capture_run_token + "\n")
        self.append_history(f"CAPTURE_RUN_TOKEN={self.capture_run_token}")
        rc = self.start_cmd("SIM3_V3_5_CAPTURE_AND_RUN.cmd")
        if rc != 0:
            self.failure_reason = f"CAPTURE_START_RC_{rc}"
            return False
        if not self.wait_capture_done(self.capture_run_token):
            return False
        if self.stop_after_current:
            return True
        self.last_report = self.report_from_capture_result()
        if not self.last_report:
            self.failure_reason = "LATEST_FULL_REPORT_NOT_FOUND_AFTER_CAPTURE"
            return False
        self.save_pending_delivery(
            self.last_report,
            "CAPTURE_COMPLETED_REPORT_PENDING_DELIVERY",
            phase="WAITING_DELIVERY",
        )
        return True

    def one_loop(self) -> bool:
        self.append_history("LOOP_START")
        self.state = "LOOP_START"
        self.write_status("RUNNING", "LOOP_START")
        if self.current_loop > 1:
            self.state = "INTER_LOOP_UI_SETTLE"
            self.write_status("RUNNING", self.state)
            time.sleep(self.inter_loop_settle_seconds)
        if not self.capture_and_run_task():
            return False
        if self.stop_after_current:
            self.append_history("NO_NEXT_COMMAND_TERMINAL_RESPONSE")
            return True
        if not self.deliver_and_wait_response(self.last_report):
            return False
        self.append_history("LOOP_OK")
        return True

    def resume_pending_if_needed(self) -> bool:
        report, phase = self.load_pending_delivery()
        if not report:
            return True
        self.current_loop = 0
        self.last_report = report
        if phase == "WAITING_RESPONSE":
            self.state = "AUTO_RESUME_PENDING_RESPONSE"
            self.append_history(f"AUTO_RESUME_PENDING_RESPONSE REPORT={report}")
            self.write_status("RUNNING", self.state)
            if not self.wait_response_with_retry():
                self.save_pending_delivery(
                    report,
                    "AUTO_RESUME_RESPONSE_NOT_YET_CONFIRMED",
                    phase="WAITING_RESPONSE",
                )
                return False
            self.clear_pending_delivery()
            return True
        self.state = "AUTO_RESUME_PENDING_DELIVERY"
        self.append_history(f"AUTO_RESUME_PENDING_DELIVERY REPORT={report}")
        self.write_status("RUNNING", self.state)
        return self.deliver_and_wait_response(report)

    def run(self) -> int:
        self.write_status("RUNNING", "STARTING")
        if self.run_cmd("SIM3_V4_START_DASHBOARD.cmd") != 0:
            self.failure_reason = "DASHBOARD_START_FAILED"
            self.write_status("FAILED", self.failure_reason)
            self.write_stop_diagnostic(self.failure_reason)
            return 1
        if not self.resume_pending_if_needed():
            self.write_status("FAILED", self.failure_reason)
            self.write_stop_diagnostic(self.failure_reason)
            return 1
        for index in range(1, self.max_loops + 1):
            self.current_loop = index
            if not self.one_loop():
                self.write_status("FAILED", self.failure_reason)
                self.write_stop_diagnostic(self.failure_reason)
                return 1
            if self.stop_after_current:
                self.state = "NO_NEXT_COMMAND_TERMINAL_RESPONSE"
                self.write_status("OK", "NO_NEXT_COMMAND_TERMINAL_RESPONSE")
                self.append_history("STOPPED_NO_NEXT_COMMAND_TERMINAL_RESPONSE")
                return 0
        self.state = "ALL_LOOPS_COMPLETED"
        self.write_status("OK", "ALL_LOOPS_COMPLETED")
        self.append_history("ALL_LOOPS_COMPLETED")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--max-loops", type=int, default=1)
    parser.add_argument("--mode", default="CAPTURE_DELIVER_WAIT_UNIFIED")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    controller = LoopController(root=root, max_loops=max(1, args.max_loops), mode=args.mode)
    try:
        return controller.run()
    except Exception as exc:
        controller.state = "UNHANDLED_CONTROLLER_EXCEPTION"
        controller.failure_reason = f"UNHANDLED_{type(exc).__name__}:{exc}"
        try:
            controller.write_status("FAILED", controller.failure_reason)
            controller.write_stop_diagnostic(controller.failure_reason)
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
