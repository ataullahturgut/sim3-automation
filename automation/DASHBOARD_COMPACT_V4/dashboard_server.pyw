from __future__ import annotations

import ctypes
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import traceback
import urllib.parse
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
AUTOMATION_ROOT = ROOT.parent

STATE_PATH = ROOT / "state.json"
STOP_FLAG = AUTOMATION_ROOT / "STOP.flag"
ERROR_LOG = ROOT / "dashboard_server_error.log"

CAPTURE_RESULT = AUTOMATION_ROOT / "CAPTURE" / "LAST_CAPTURE_RESULT.txt"
DELIVERY_RESULT = AUTOMATION_ROOT / "DELIVERY" / "LAST_DELIVERY_RESULT.txt"
RESPONSE_RESULT = AUTOMATION_ROOT / "RESPONSE" / "LAST_RESPONSE_WAIT_RESULT.txt"
LOOP_RESULT = AUTOMATION_ROOT / "LOOP" / "LAST_LOOP_RESULT.txt"
TASK_FILE = AUTOMATION_ROOT / "INBOX" / "TASK.txt"
LATEST_READY = AUTOMATION_ROOT / "REPORTS" / "LATEST_READY.json"
REPORTS_DIR = AUTOMATION_ROOT / "REPORTS"
RUNTIME_DIR = AUTOMATION_ROOT / "RUNTIME"

HOST = "127.0.0.1"
PORT = 8767

STAGE_LABELS = {
    1: "GPT görevi/cevabı bekleniyor",
    2: "Görev yakalanıyor",
    3: "Codex'e gönderiliyor",
    4: "Codex çalışıyor",
    5: "Rapor üretiliyor",
    6: "Rapor GPT'ye yükleniyor",
}
FAILURE_WORDS = ("BLOCKED", "FAILED", "TIMEOUT", "ERROR", "PAUSED")


def safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def parse_key_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("=====") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().upper()] = value.strip()
    return values


def parse_task() -> tuple[str, str]:
    text = read_text(TASK_FILE)
    if not text:
        return "YENİ GÖREV", "ChatGPT komutu bekleniyor"

    task_id = ""
    step = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("# TASK_ID="):
            task_id = line.split("=", 1)[1].strip()
        elif line.startswith("# STEP="):
            step = line.split("=", 1)[1].strip()

    objective = ""
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip().upper() == "OBJECTIVE:":
            for candidate in lines[index + 1 :]:
                value = candidate.strip()
                if value:
                    objective = value
                    break
            break

    display_id = task_id or step or "YENİ GÖREV"
    display_title = objective or step.replace("_", " ").strip() or "Otomasyon görevi yürütülüyor"
    return display_id, display_title


def load_state() -> dict[str, Any]:
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def atomic_state_write(data: dict[str, Any]) -> None:
    fd, temporary = tempfile.mkstemp(
        prefix="state_",
        suffix=".json.tmp",
        dir=str(ROOT),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, STATE_PATH)
    finally:
        try:
            if os.path.exists(temporary):
                os.unlink(temporary)
        except OSError:
            pass


def format_elapsed(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d} sa {minutes:02d} dk"
    return f"{minutes:02d} dk {secs:02d} sn"


def newest_runtime_files() -> tuple[Path | None, Path | None, float]:
    newest_metadata: Path | None = None
    newest_events: Path | None = None
    newest_time = 0.0

    try:
        runtime_dirs = [
            item for item in RUNTIME_DIR.iterdir()
            if item.is_dir()
        ]
    except OSError:
        return None, None, 0.0

    for runtime in runtime_dirs:
        metadata = runtime / "run_metadata.json"
        events = runtime / "codex_events.jsonl"
        candidate_time = max(safe_mtime(metadata), safe_mtime(events), safe_mtime(runtime))

        if candidate_time > newest_time:
            newest_time = candidate_time
            newest_metadata = metadata if metadata.is_file() else None
            newest_events = events if events.is_file() else None

    return newest_metadata, newest_events, newest_time


def newest_report() -> tuple[Path | None, float]:
    report_path: Path | None = None
    report_time = 0.0

    try:
        ready = json.loads(LATEST_READY.read_text(encoding="utf-8-sig"))
        filename = str(ready.get("report_filename") or "").strip()
        if filename:
            candidate = REPORTS_DIR / filename
            if candidate.is_file():
                report_path = candidate
                report_time = safe_mtime(candidate)
    except Exception:
        pass

    if report_path is not None:
        return report_path, report_time

    try:
        for candidate in REPORTS_DIR.glob("*_FULL.txt"):
            candidate_time = safe_mtime(candidate)
            if candidate_time > report_time:
                report_path = candidate
                report_time = candidate_time
    except OSError:
        pass

    return report_path, report_time


def capture_stage(values: dict[str, str]) -> int:
    combined = " ".join(
        values.get(key, "")
        for key in ("LAST_STATE", "RESULT_REASON", "FINAL_STATUS")
    ).upper()

    if any(token in combined for token in ("RUNNER_COMPLETED", "REPORT_READY", "REPORT_PRODUCED")):
        return 5
    if any(token in combined for token in ("CODEX", "RUNNER_STARTED", "RUNNER_RUNNING", "WORKER_STARTED")):
        return 4
    if any(token in combined for token in ("TASK_CAPTURED", "COMMAND_CAPTURED", "CLIPBOARD_CAPTURED")):
        return 2
    return 1


def failure_from_result(values: dict[str, str]) -> str:
    status = values.get("FINAL_STATUS", "").upper()
    reason = values.get("RESULT_REASON", "") or values.get("FAILURE_REASON", "")

    if any(word in status for word in FAILURE_WORDS):
        return reason or status
    return ""


class DashboardStateMonitor(threading.Thread):
    def __init__(self) -> None:
        super().__init__(name="SIM3DashboardStateMonitor", daemon=True)
        self.session_started = time.time()
        self.activity_floor = self.session_started - 8.0
        self.cycle_started: float | None = None
        self.last_task_mtime = 0.0
        self.last_written_signature = ""

    def fresh(self, path: Path) -> bool:
        return safe_mtime(path) >= self.activity_floor

    def build_state(self) -> dict[str, Any]:
        current = load_state()

        if STOP_FLAG.exists():
            current.update(
                {
                    "overall_status": "stopped",
                    "state_label": "DURDU",
                    "needs_attention": True,
                }
            )
            current.setdefault(
                "stop_reason",
                "Kullanıcı otomasyonu durdurdu.",
            )
            return current

        candidates: list[tuple[float, int, int]] = []

        task_time = safe_mtime(TASK_FILE)
        if task_time >= self.activity_floor:
            candidates.append((task_time, 20, 2))
            if task_time > self.last_task_mtime:
                self.last_task_mtime = task_time
                self.cycle_started = task_time

        metadata, events, runtime_time = newest_runtime_files()
        if runtime_time >= self.activity_floor:
            if metadata is not None:
                candidates.append((safe_mtime(metadata), 30, 3))
            if events is not None and safe_size(events) > 0:
                candidates.append((safe_mtime(events), 40, 4))

        capture_values: dict[str, str] = {}
        if self.fresh(CAPTURE_RESULT):
            capture_values = parse_key_values(CAPTURE_RESULT)
            candidates.append(
                (
                    safe_mtime(CAPTURE_RESULT),
                    45,
                    capture_stage(capture_values),
                )
            )

        report_path, report_time = newest_report()
        if report_time >= self.activity_floor:
            candidates.append((report_time, 50, 5))

        delivery_values: dict[str, str] = {}
        if self.fresh(DELIVERY_RESULT):
            delivery_values = parse_key_values(DELIVERY_RESULT)
            candidates.append((safe_mtime(DELIVERY_RESULT), 60, 6))

        response_values: dict[str, str] = {}
        if self.fresh(RESPONSE_RESULT):
            response_values = parse_key_values(RESPONSE_RESULT)
            candidates.append((safe_mtime(RESPONSE_RESULT), 70, 1))

        loop_values: dict[str, str] = {}
        if self.fresh(LOOP_RESULT):
            loop_values = parse_key_values(LOOP_RESULT)

        controller_status = loop_values.get("FINAL_STATUS", "").upper()
        controller_reason = (
            loop_values.get("RESULT_REASON", "")
            or loop_values.get("FAILURE_REASON", "")
        )
        controller_running = controller_status == "RUNNING"
        controller_failed = any(word in controller_status for word in FAILURE_WORDS)

        # The unified loop controller owns retry policy. A capture/delivery/response
        # child may briefly write FAILED or PAUSED before the controller retries it.
        # While the controller is RUNNING, those child states are diagnostic only
        # and must not flash the dashboard to DURDU. A terminal controller failure
        # remains authoritative.
        if controller_failed:
            failure_reason = controller_reason or controller_status
        elif controller_running:
            failure_reason = ""
        else:
            failure_reason = (
                failure_from_result(response_values)
                or failure_from_result(delivery_values)
                or failure_from_result(capture_values)
            )

        if failure_reason:
            current.update(
                {
                    "overall_status": "stopped",
                    "state_label": "DURDU",
                    "needs_attention": True,
                    "stop_reason": failure_reason,
                }
            )
            return current

        stage = 1
        if candidates:
            _, _, stage = max(candidates, key=lambda item: (item[0], item[1]))

        task_id, task_title = parse_task()
        if task_time < self.activity_floor:
            task_id = "YENİ GÖREV"
            task_title = "ChatGPT komutu bekleniyor"

        elapsed = 0.0
        if self.cycle_started is not None:
            elapsed = time.time() - self.cycle_started

        current.update(
            {
                "overall_status": "running",
                "state_label": "RUNNING",
                "needs_attention": False,
                "cycle_stage": stage,
                "cycle_stage_label": STAGE_LABELS[stage],
                "active_task_id": task_id,
                "active_task_title": task_title,
                "elapsed_text": format_elapsed(elapsed),
                "stop_reason": "",
                "steps": [STAGE_LABELS[index] for index in range(1, 7)],
            }
        )

        if report_path is not None:
            current["report_path"] = str(report_path)

        return current

    def run(self) -> None:
        while True:
            try:
                state = self.build_state()
                signature = json.dumps(state, ensure_ascii=False, sort_keys=True)

                if signature != self.last_written_signature:
                    atomic_state_write(state)
                    self.last_written_signature = signature

            except Exception:
                ERROR_LOG.write_text(
                    "MONITOR_ERROR\n" + traceback.format_exc(),
                    encoding="utf-8",
                )

            time.sleep(0.5)


def reveal(path_text: str, select_file: bool = False) -> None:
    if not path_text:
        return

    path = Path(path_text)

    try:
        if select_file and path.is_file():
            subprocess.Popen(["explorer.exe", f"/select,{path}"])
        elif path.exists():
            os.startfile(str(path))
        elif path.parent.exists():
            os.startfile(str(path.parent))
    except Exception:
        pass


def send_stop_hotkey() -> None:
    if os.name != "nt":
        return

    user32 = ctypes.windll.user32
    key_up = 0x0002
    vk_control, vk_menu, vk_x = 0x11, 0x12, 0x58

    user32.keybd_event(vk_control, 0, 0, 0)
    user32.keybd_event(vk_menu, 0, 0, 0)
    user32.keybd_event(vk_x, 0, 0, 0)
    user32.keybd_event(vk_x, 0, key_up, 0)
    user32.keybd_event(vk_menu, 0, key_up, 0)
    user32.keybd_event(vk_control, 0, key_up, 0)


def request_stop() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    STOP_FLAG.write_text(
        "SOURCE=COMPACT_DASHBOARD\n"
        f"REQUESTED_AT={timestamp}\n"
        "REASON=USER_REQUESTED_GRACEFUL_STOP\n",
        encoding="ascii",
    )

    state = load_state()
    state.update(
        {
            "overall_status": "stopped",
            "state_label": "DURDU",
            "needs_attention": True,
            "stop_reason": "Kullanıcı dashboard üzerinden güvenli durdurma istedi.",
        }
    )
    atomic_state_write(state)
    send_stop_hotkey()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *_args: Any) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header(
            "Cache-Control",
            "no-store, no-cache, must-revalidate, max-age=0",
        )
        super().end_headers()

    def send_plain(self, code: int, value: str) -> None:
        body = value.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_action(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        kind = (urllib.parse.parse_qs(parsed.query).get("kind") or [""])[0]
        state = load_state()

        if kind == "diagnostic":
            reveal(str(state.get("diagnostic_file", "")))
            self.send_plain(200, "OK")
            return

        if kind == "report":
            reveal(str(state.get("report_path", "")), True)
            self.send_plain(200, "OK")
            return

        if kind == "stop":
            request_stop()
            self.send_plain(200, "STOP_REQUESTED")
            return

        self.send_plain(400, "UNKNOWN_ACTION")

    def do_POST(self) -> None:
        if urllib.parse.urlparse(self.path).path == "/action":
            self.handle_action()
            return
        self.send_plain(404, "NOT_FOUND")

    def do_GET(self) -> None:
        if urllib.parse.urlparse(self.path).path == "/health":
            self.send_plain(200, "OK")
            return

        if urllib.parse.urlparse(self.path).path == "/action":
            self.handle_action()
            return

        super().do_GET()


def main() -> None:
    os.chdir(ROOT)
    DashboardStateMonitor().start()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048 or getattr(exc, "errno", None) in {48, 98}:
            raise SystemExit(0)

        ERROR_LOG.write_text(
            traceback.format_exc(),
            encoding="utf-8",
        )
        raise

    except BaseException:
        ERROR_LOG.write_text(
            traceback.format_exc(),
            encoding="utf-8",
        )
        raise
