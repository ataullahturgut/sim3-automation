# SIM3 Automation

SIM3 Automation is a Windows desktop automation workflow that captures a task from ChatGPT, runs the configured Codex workflow, tracks execution, delivers the generated report, and waits for the next response.

## Quick start

1. Install the prerequisites listed in [`docs/INSTALLATION.md`](docs/INSTALLATION.md).
2. Open `automation/CONFIG/sim3_v3_config.json` and set `repo` to your own project folder.
3. Calibrate `automation/CONFIG/UI_COORDINATES.ini` by following [`docs/COORDINATE_CALIBRATION.md`](docs/COORDINATE_CALIBRATION.md). The public values are intentionally set to `0` and must be replaced before a full run.
4. Open ChatGPT in the calibrated browser position and run **`START_DASHBOARD.cmd`** to verify the dashboard.
5. Perform the first full run with a harmless read-only task by running **`START_SIM3.cmd`**.

To open only the dashboard, run **`START_DASHBOARD.cmd`**.

## Repository structure

```text
SIM3_AUTOMATION_PUBLIC_RELEASE/
├─ START_SIM3.cmd              Main launcher
├─ START_DASHBOARD.cmd         Dashboard-only launcher
├─ README.md                   Project overview
├─ SECURITY.md                 Security guidance
├─ PRIVACY.md                  Local-data handling notes
├─ docs/                       Installation, coordinate calibration, and troubleshooting
└─ automation/                 Application runtime and source files
```

## First-run warning

The public package is not pre-calibrated for another computer. All interface coordinates are deliberately reset to `0`. Before running the full workflow, users must configure their project path and calibrate the ChatGPT attachment, file-menu, send-button, and scrolling coordinates. Browser zoom, Windows display scaling, monitor layout, and browser position must remain consistent with calibration.

## Runtime data

The following directories are intentionally empty in the public release and are excluded from Git:

- `automation/REPORTS`
- `automation/LOGS`
- `automation/RUNTIME`
- `automation/RECOVERY`
- `automation/INBOX`

Browser profiles, generated reports, task captures, logs, recovery artifacts, and local runtime tokens are not included in this distribution.

## Platform

- Windows 10 or Windows 11
- PowerShell
- Python 3
- AutoHotkey v2
- Google Chrome or Microsoft Edge, according to the local configuration

## Release status

This package was created from the existing SIM3 V4.7 automation without rebuilding the automation engine. Machine-specific paths and runtime artifacts were removed from the public distribution.

## License

No open-source license has been selected yet. Until a license file is added, normal copyright restrictions apply. Do not assume permission to redistribute or modify the project beyond what the repository owner explicitly grants.
