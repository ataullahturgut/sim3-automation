# Coordinate Calibration

SIM3 Automation interacts with parts of the ChatGPT interface by using screen coordinates. The public release intentionally ships with all coordinates set to `0` because coordinates from the original computer would not be reliable on another computer.

## Configuration file

Edit:

```text
automation/CONFIG/UI_COORDINATES.ini
```

Default public-release values:

```ini
[Environment]
ScreenWidth=1920
ScreenHeight=1080

[Coordinates]
ATTACH_X=0
ATTACH_Y=0
FILE_ITEM_X=0
FILE_ITEM_Y=0
SEND_X=0
SEND_Y=0
SCROLL_X=0
SCROLL_Y=0
```

Do not start a full automation run while the required coordinates are still `0`.

## Coordinate meanings

| Setting | Purpose |
|---|---|
| `ATTACH_X`, `ATTACH_Y` | Center of the ChatGPT attachment or plus button used to open the file menu. |
| `FILE_ITEM_X`, `FILE_ITEM_Y` | Center of the file-upload item after the attachment menu opens. |
| `SEND_X`, `SEND_Y` | Center of the ChatGPT send button. |
| `SCROLL_X`, `SCROLL_Y` | A safe point inside the answer panel where scrolling can be performed without clicking a control. |

## Recommended display setup

Coordinate-based automation is sensitive to layout changes. Before calibration:

1. Use one primary monitor during initial setup.
2. Keep Windows display scaling at a stable value, preferably `100%` when possible.
3. Keep browser zoom at `100%`.
4. Use the same browser window size and position for calibration and normal operation.
5. Keep the ChatGPT sidebar and interface layout in a consistent state.
6. Avoid changing theme, browser zoom, display scaling, or monitor arrangement after calibration.
7. Do not move the target browser window while the automation is running.

The automation may still work at other scaling or zoom values, but coordinates and image templates must be calibrated for those exact settings.

## How to obtain coordinates

Use AutoHotkey v2 Window Spy:

1. Install AutoHotkey v2.
2. Open the AutoHotkey installation folder or right-click the AutoHotkey tray icon.
3. Start **Window Spy**.
4. Open ChatGPT in the browser and place the browser exactly where it will be used.
5. Move the mouse pointer to the center of the required interface element.
6. Read the screen coordinates shown by Window Spy.
7. Enter the X and Y values in `UI_COORDINATES.ini`.

Use screen coordinates, not coordinates relative to the active window, unless the local automation version has explicitly been changed to use window-relative coordinates.

## Calibration sequence

### 1. Attachment button

Move the pointer to the center of the ChatGPT attachment or plus button. Record the screen coordinates as:

```ini
ATTACH_X=<measured X>
ATTACH_Y=<measured Y>
```

### 2. File-upload menu item

Click the attachment button manually so its menu opens. Move the pointer to the center of the option that opens the file-selection dialog. Record:

```ini
FILE_ITEM_X=<measured X>
FILE_ITEM_Y=<measured Y>
```

### 3. Send button

Place sample text in the ChatGPT input area so that the send button is visible. Move the pointer to its center and record:

```ini
SEND_X=<measured X>
SEND_Y=<measured Y>
```

### 4. Scroll point

Move the pointer to an empty, safe area inside the response panel. The point must not overlap a link, copy button, menu, attachment, scrollbar handle, or other clickable control. Record:

```ini
SCROLL_X=<measured X>
SCROLL_Y=<measured Y>
```

## Environment values

Update these values to match the primary display used during automation:

```ini
ScreenWidth=<display width>
ScreenHeight=<display height>
```

Examples:

- Full HD: `1920` × `1080`
- QHD: `2560` × `1440`
- 4K UHD: `3840` × `2160`

These values document the calibration environment and help diagnose mismatched configurations.

## Verification before a full run

Before starting `START_SIM3.cmd`:

1. Confirm no required coordinate remains `0`.
2. Confirm the browser is on the same monitor used during calibration.
3. Confirm Windows scaling and browser zoom have not changed.
4. Confirm ChatGPT is open, signed in, and visible.
5. Confirm no other window covers the attachment, send, or response areas.
6. Test the dashboard separately with `START_DASHBOARD.cmd`.
7. Perform the first automation run with a harmless read-only task.

## Recalibration is required when

Recalibrate after any of the following:

- Changing monitor resolution or monitor arrangement.
- Changing Windows display scaling.
- Changing browser zoom.
- Moving the browser to a monitor with different scaling.
- Changing the browser window size or normal working position.
- A major ChatGPT interface update.
- The automation clicks beside a button or opens the wrong menu.

## Safety note

Coordinate automation can click the wrong location when the interface changes. Keep the first test non-destructive and watch the browser during calibration. Stop the automation immediately if the pointer targets an unexpected control.
