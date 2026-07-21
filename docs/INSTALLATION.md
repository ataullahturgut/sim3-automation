# Installation and First-Time Setup

## 1. Download and extract

Download the repository or a release ZIP and extract it to a normal writable folder.

Do not run the automation directly from inside a ZIP archive. Avoid protected folders such as `C:\Program Files` unless you understand the required permissions.

A simple path is recommended, for example:

```text
C:\SIM3_Automation
```

## 2. Prerequisites

Install and verify:

- Windows 10 or Windows 11.
- Python 3 available from the command line.
- AutoHotkey v2.
- PowerShell 5.1 or later.
- Google Chrome or Microsoft Edge.
- Any command-line tools required by the configured Codex workflow.
- A valid signed-in ChatGPT browser session when the workflow requires it.

Basic checks:

```powershell
python --version
powershell -NoProfile -Command "$PSVersionTable.PSVersion"
```

AutoHotkey **v2** is required; v1 syntax is not compatible with these scripts.

## 3. Configure the target project

Edit:

```text
automation/CONFIG/sim3_v3_config.json
```

Replace:

```json
"repo": "C:/PATH/TO/YOUR/PROJECT"
```

with the absolute path of the project that SIM3 may inspect or process.

Example:

```json
"repo": "C:/Users/YourName/Documents/MyProject"
```

Use forward slashes in JSON or escape Windows backslashes correctly. Confirm the folder exists before starting the automation.

Review the remaining configuration options before use. The public release defaults to a read-only-oriented mode, but users remain responsible for verifying the effective workflow and permissions.

## 4. Calibrate the user interface

Edit:

```text
automation/CONFIG/UI_COORDINATES.ini
```

All public-release coordinates are intentionally set to `0`. They are placeholders and cannot be expected to work on another computer.

Do not perform a full automation run until the required values have been calibrated.

Detailed calibration instructions are available in:

```text
docs/COORDINATE_CALIBRATION.md
```

The values represent:

- `ATTACH_X` / `ATTACH_Y`: ChatGPT attachment or plus button.
- `FILE_ITEM_X` / `FILE_ITEM_Y`: file-upload item in the attachment menu.
- `SEND_X` / `SEND_Y`: ChatGPT send button.
- `SCROLL_X` / `SCROLL_Y`: safe scrolling point in the response panel.

For initial setup, use a stable browser window, `100%` browser zoom, and preferably `100%` Windows display scaling.

## 5. Prepare the browser

Before starting:

1. Open the supported browser.
2. Sign in to ChatGPT.
3. Open the intended conversation or working page.
4. Place the browser on the monitor and at the position used during calibration.
5. Keep the relevant ChatGPT controls visible.
6. Ensure no other application covers the target areas.

The public package does not contain or distribute a browser profile. Each user must use their own local browser session.

## 6. Start the dashboard first

Run:

```text
START_DASHBOARD.cmd
```

Confirm the dashboard opens without referencing an old or machine-specific folder.

Close it or leave it running according to the local workflow.

## 7. Perform a safe first run

Use a harmless read-only task for the first run. Avoid production repositories and destructive instructions until capture, execution, report delivery, and response detection have been verified.

Start the full workflow with:

```text
START_SIM3.cmd
```

Watch the first run. Stop the automation if it clicks an unexpected interface element.

## 8. Runtime directories

The public release intentionally includes empty runtime directories:

```text
automation/INBOX
automation/REPORTS
automation/LOGS
automation/RUNTIME
automation/RECOVERY
```

They may contain private task text, project paths, reports, logs, captured responses, or recovery data after use. Do not commit their generated contents to GitHub.

The included `.gitignore` is designed to exclude these artifacts, but users should still review staged files before every commit.

## Updating the automation

Back up local configuration before replacing a release:

```text
automation/CONFIG/sim3_v3_config.json
automation/CONFIG/UI_COORDINATES.ini
```

Do not copy old reports, logs, browser profiles, or runtime state into a public release.
