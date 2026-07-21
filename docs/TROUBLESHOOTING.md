# Troubleshooting

## The dashboard does not open

- Confirm Python is installed and available from the command line.
- Run `python --version` in PowerShell.
- Review the launcher under `automation/DASHBOARD_COMPACT_V4`.
- Check whether Windows Security or antivirus software blocked a script.
- Confirm the package was extracted from the ZIP before running.

## The automation starts but does not click anything

- Confirm AutoHotkey v2 is installed.
- Confirm the required coordinate values in `automation/CONFIG/UI_COORDINATES.ini` are not `0`.
- Confirm the browser is on the same monitor used during calibration.
- Confirm browser zoom and Windows display scaling match the calibration environment.
- Confirm no other window covers ChatGPT.

See `docs/COORDINATE_CALIBRATION.md`.

## The automation clicks the wrong location

This normally indicates a coordinate or layout mismatch.

Recalibrate after changing:

- Browser window position or size.
- Monitor resolution.
- Windows display scaling.
- Browser zoom.
- Monitor arrangement.
- ChatGPT sidebar or page layout.

Use a safe read-only task while verifying new coordinates.

## The attachment menu opens, but file selection fails

- Verify `ATTACH_X` and `ATTACH_Y` target the center of the attachment or plus button.
- Open the menu manually and verify `FILE_ITEM_X` and `FILE_ITEM_Y` target the correct upload option.
- Check whether the menu layout changed after a ChatGPT update.
- Confirm browser zoom is unchanged.

## The task is not captured

- Confirm ChatGPT is open, signed in, and visible.
- Check AutoHotkey v2.
- Check browser zoom, Windows scaling, window position, and coordinates.
- Confirm the expected copy icon or response panel is visible.
- Review local logs for the last capture status.

## Copy-icon or image detection fails

The automation uses template images under:

```text
automation/CAPTURE
automation/DELIVERY/TEMPLATES
```

Image matching can fail because of:

- ChatGPT interface updates.
- Light/dark theme differences.
- Browser zoom changes.
- Windows scaling changes.
- Different font rendering.
- A template captured at another resolution.

Restore the expected layout or replace the local template with a clean crop captured under the current environment. Do not publish screenshots containing private conversations.

## The send button is not clicked

- Confirm text is present in the ChatGPT input area.
- Recheck `SEND_X` and `SEND_Y`.
- Confirm the send button has not changed position.
- Confirm the browser window is not maximized, restored, or moved differently from calibration.

## Scrolling is slow or does not work

- Verify `SCROLL_X` and `SCROLL_Y` point to an empty part of the response panel.
- Do not place the scroll point over a button, link, code block control, or scrollbar handle.
- Confirm the target browser window has focus.
- Recalibrate after layout changes.

## Reports are not delivered

- Inspect locally generated files under `automation/LOGS`, `automation/RUNTIME`, and `automation/REPORTS`.
- Check whether the expected report file was created.
- Confirm the attachment menu and file item coordinates.
- Confirm the browser remained visible and signed in.

When opening a public issue, do not upload raw logs or reports without reviewing them. Redact project names, user paths, task text, account information, and report content.

## The configured project cannot be found

Open:

```text
automation/CONFIG/sim3_v3_config.json
```

Confirm that `repo` contains an existing absolute folder path. JSON syntax must remain valid.

## Windows blocks a script

Windows may mark files downloaded from the internet as blocked.

- Right-click the ZIP before extraction, open **Properties**, and use **Unblock** when available.
- Only run scripts obtained from a source you trust.
- Review PowerShell execution policy and local security policy.
- Do not permanently weaken system security merely to run the automation.

## A public Git commit contains runtime files

Stop before pushing. Review staged files:

```powershell
git status
git diff --cached
```

Remove generated reports, logs, runtime files, recovery artifacts, browser data, and project-specific configuration from the commit. The public repository should not contain private execution history.
