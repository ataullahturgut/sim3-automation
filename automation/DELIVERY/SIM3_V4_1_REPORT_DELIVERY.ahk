#Requires AutoHotkey v2.0
#SingleInstance Force
#ErrorStdOut
OnError(SIM3_FullFixUnhandledErrorV3)
CoordMode "Mouse", "Screen"
CoordMode "Pixel", "Screen"
SetTitleMatchMode 2

global Root := A_Args.Length >= 1 ? RTrim(A_Args[1], "\/") : A_ScriptDir "\.."
global ReportsDir := Root "\REPORTS"
global DeliveryDir := Root "\DELIVERY"
global ConfigDir := Root "\CONFIG"
global TemplateDir := Root "\DELIVERY\TEMPLATES"
global ResultPath := DeliveryDir "\LAST_DELIVERY_RESULT.txt"
global DeliveryTokenPath := DeliveryDir "\CURRENT_DELIVERY_TOKEN.txt"
global DeliveryReportPath := DeliveryDir "\CURRENT_DELIVERY_REPORT.txt"
global UiIni := ConfigDir "\UI_COORDINATES.ini"
global PlusIconTemplate := TemplateDir "\SIM3_CHATGPT_PLUS_ICON_TEMPLATE.png"
global ReportDocumentTemplate := TemplateDir "\SIM3_CHATGPT_REPORT_DOCUMENT_ICON_TEMPLATE.png"

global DeliveryRunToken := ReadTextFileTrimmed(DeliveryTokenPath)
global StartedAt := A_Now
global StartTick := A_TickCount
global BrowserHwndUsed := 0
global BrowserTitleUsed := ""
global SourceReport := ""
global SourceReportSelection := "NONE"
global AttachMode := "NONE"
global AttachClicked := false
global FileMenuClicked := false
global FileDialogOpened := false
global FilePathSet := false
global FilePathSetMethod := "NONE"
global FileDialogTitle := ""
global FileDialogProcess := ""
global FileDialogControlSummary := ""
global FileDialogClosed := false
global AttachmentReady := false
global AttachmentReadyPollCount := 0
global AttachmentStablePollCount := 0
global SendClicked := false
global SendClickMode := "NONE"
global PlusSearchCount := 0
global PlusFoundCount := 0
global DocumentSearchCount := 0
global DocumentFoundCount := 0
global LastState := "INITIALIZING"

Hotkey "^!x", EmergencyStop

if !DirExist(DeliveryDir)
    DirCreate DeliveryDir

WriteStatus("STARTING", "INITIALIZING")

if (DeliveryRunToken = "")
    Finish("FAILED", "DELIVERY_RUN_TOKEN_NOT_FOUND", 40)

SourceReport := ResolveDeliverySource()

if (SourceReport = "")
    Finish("FAILED", "LATEST_FULL_REPORT_NOT_FOUND", 41)

if !FileExist(SourceReport)
    Finish("FAILED", "SOURCE_REPORT_NOT_FOUND", 42)

if FileGetSize(SourceReport) <= 0
    Finish("FAILED", "SOURCE_REPORT_EMPTY", 43)

if !FileExist(PlusIconTemplate)
    Finish("FAILED", "PLUS_ICON_TEMPLATE_NOT_FOUND", 44)

if !FileExist(ReportDocumentTemplate)
    Finish("FAILED", "REPORT_DOCUMENT_TEMPLATE_NOT_FOUND", 45)

AttachX := Integer(IniRead(UiIni, "Coordinates", "ATTACH_X", "-1"))
AttachY := Integer(IniRead(UiIni, "Coordinates", "ATTACH_Y", "-1"))
FileItemX := Integer(IniRead(UiIni, "Coordinates", "FILE_ITEM_X", "-1"))
FileItemY := Integer(IniRead(UiIni, "Coordinates", "FILE_ITEM_Y", "-1"))
SendX := Integer(IniRead(UiIni, "Coordinates", "SEND_X", "-1"))
SendY := Integer(IniRead(UiIni, "Coordinates", "SEND_Y", "-1"))

BrowserHwnd := FindBrowserWindow()

if !BrowserHwnd
    Finish("FAILED", "CHATGPT_BROWSER_WINDOW_NOT_FOUND", 46)

BrowserHwndUsed := BrowserHwnd
BrowserTitleUsed := WinGetTitle("ahk_id " BrowserHwnd)

WinActivate "ahk_id " BrowserHwnd

if !WinWaitActive("ahk_id " BrowserHwnd, , 5)
    Finish("FAILED", "BROWSER_ACTIVATION_FAILED", 47)

ScrollToBottom(BrowserHwnd)
Sleep 900

AttachPointX := -1
AttachPointY := -1

if FindPlusIcon(BrowserHwnd, &AttachPointX, &AttachPointY)
{
    AttachMode := "DYNAMIC_PLUS_IMAGE_SEARCH"
}
else if PointInsideBrowser(AttachX, AttachY, BrowserHwnd)
{
    AttachPointX := AttachX
    AttachPointY := AttachY
    AttachMode := "FIXED_UI_COORDINATE_FALLBACK"
}
else
{
    Finish("PAUSED", "ATTACH_BUTTON_NOT_FOUND", 20)
}

LastState := "CLICKING_ATTACH"
WriteStatus("ATTACH_MENU", "ATTACH_POINT_READY")
MouseMove AttachPointX, AttachPointY, 15
Sleep 300
Click AttachPointX, AttachPointY
AttachClicked := true
Sleep 900

LastState := "CLICKING_FILE_MENU"
WriteStatus("FILE_MENU", "OPENING_FILE_DIALOG_ROBUST")

DialogHwnd := OpenFileDialogRobust(BrowserHwnd, AttachPointX, AttachPointY, FileItemX, FileItemY)

if !DialogHwnd
    Finish("PAUSED", "FILE_DIALOG_NOT_OPENED_AFTER_ROBUST_MENU_ATTEMPTS", 22)

FileDialogOpened := true
FileDialogTitle := WinGetTitle("ahk_id " DialogHwnd)
FileDialogProcess := WinGetProcessName("ahk_id " DialogHwnd)
WinActivate "ahk_id " DialogHwnd
Sleep 500

PathResult := SetFileDialogPathRobust(DialogHwnd, SourceReport)
FilePathSetMethod := PathResult["method"]
FileDialogControlSummary := PathResult["controls"]

if !PathResult["ok"]
    Finish("FAILED", "FILE_DIALOG_PATH_SET_FAILED_ALL_METHODS", 48)

FilePathSet := true

if PathResult["dialog_closed"]
{
    FileDialogClosed := true
}
else
{
    Sleep 350
    SendEvent "{Enter}"

    if !WinWaitClose("ahk_id " DialogHwnd, , 15)
        Finish("FAILED", "FILE_DIALOG_DID_NOT_CLOSE", 49)

    FileDialogClosed := true
}
WinActivate "ahk_id " BrowserHwnd

if !WinWaitActive("ahk_id " BrowserHwnd, , 5)
    Finish("FAILED", "BROWSER_REACTIVATION_FAILED", 50)

LastState := "WAITING_ATTACHMENT_READY"
WriteStatus("UPLOADING", "WAITING_ATTACHMENT_READY")

if !WaitForAttachmentReady(BrowserHwnd)
    Finish("PAUSED", "ATTACHMENT_OR_SEND_NOT_READY_45_SECONDS_AFTER_FOCUS_REFRESH", 23)

AttachmentReady := true
WriteStatus("ATTACHED", "ATTACHMENT_READY")

LastState := "SENDING_BY_DIRECT_BUTTON_CLICK"
if !SendAttachedReportByKeyboard(BrowserHwnd)
    Finish("PAUSED", "DIRECT_SEND_BUTTON_CLICK_FAILED", 24)

SendClicked := true
SendClickMode := "DIRECT_SEND_BUTTON_CLICK"
Sleep 1500

WriteStatus("DELIVERED", "SEND_CLICKED_REPORT_ATTACHED")
Finish("OK", "REPORT_DELIVERED_SEND_CLICKED", 0)

ReadTextFileTrimmed(Path)
{
    if !FileExist(Path)
        return ""
    try
        return Trim(FileRead(Path, "UTF-8"), " `t`r`n")
    catch
        return ""
}

ResolveDeliverySource()
{
    global DeliveryReportPath, SourceReportSelection

    ; SIM3_EXPLICIT_DELIVERY_FILE_CONTRACT_V2
    ; Priority:
    ; 1. DELIVERY_FILE from the current INBOX task.
    ; 2. CURRENT_DELIVERY_REPORT.txt pointer.
    ; 3. Latest *_FULL.txt fallback for legacy tasks.
    ExplicitFile := ResolveExplicitDeliveryFileFromTask()

    if (ExplicitFile != "")
    {
        SourceReportSelection := "TASK_DELIVERY_FILE"
        return ExplicitFile
    }

    PointerFile := ReadTextFileTrimmed(DeliveryReportPath)

    if (PointerFile != "")
    {
        PointerAttrs := FileExist(PointerFile)

        if (PointerAttrs != "") && !InStr(PointerAttrs, "D")
        {
            try
            {
                if (FileGetSize(PointerFile) > 0)
                {
                    SourceReportSelection := "CURRENT_DELIVERY_REPORT"
                    return PointerFile
                }
            }
        }
    }

    LegacyFile := FindLatestFullReport()

    if (LegacyFile != "")
        SourceReportSelection := "LATEST_FULL_REPORT_FALLBACK"

    return LegacyFile
}

ResolveExplicitDeliveryFileFromTask()
{
    global Root

    TaskPath := Root "\INBOX\TASK.txt"

    if !FileExist(TaskPath)
        return ""

    try
        TaskText := FileRead(TaskPath, "UTF-8")
    catch
        return ""

    if !RegExMatch(
        TaskText,
        "mi)^\s*DELIVERY_FILE\s*=\s*([^\r\n]+)",
        &FileMatch
    )
        return ""

    Candidate := Trim(FileMatch[1], " `t`r`n")
    Candidate := StrReplace(Candidate, "/", "\")

    ; Only absolute Windows paths are accepted.
    if !RegExMatch(Candidate, "i)^[A-Z]:\\")
        return ""

    CandidateAttrs := FileExist(Candidate)

    if (CandidateAttrs = "") || InStr(CandidateAttrs, "D")
        return ""

    try
    {
        if (FileGetSize(Candidate) <= 0)
            return ""
    }
    catch
        return ""

    ; Bounded attachment types only.
    if !RegExMatch(
        Candidate,
        "i)\.(txt|zip|csv|json|xlsx|docx|pdf)$"
    )
        return ""

    TaskId := ""

    if RegExMatch(
        TaskText,
        "mi)^\s*(?:#\s*)?TASK_ID\s*=\s*([^\r\n]+)",
        &TaskMatch
    )
        TaskId := Trim(TaskMatch[1], " `t`r`n")

    ; Prevent a stale or unrelated file from being selected.
    if (TaskId != "")
    {
        if !InStr(StrUpper(Candidate), StrUpper(TaskId))
            return ""
    }

    return Candidate
}
FindLatestFullReport()
{
    global ReportsDir

    ReadyPath := ReportsDir "\LATEST_READY.json"

    if FileExist(ReadyPath)
    {
        Text := FileRead(ReadyPath, "UTF-8")

        if RegExMatch(Text, '"report_path"\s*:\s*"([^"]+)"', &M)
        {
            Candidate := StrReplace(M[1], "\\", "\")
            if FileExist(Candidate)
                return Candidate
        }
    }

    LatestPath := ""
    LatestTime := ""

    Loop Files, ReportsDir "\*_FULL.txt", "F"
    {
        if (LatestPath = "") || (A_LoopFileTimeModified > LatestTime)
        {
            LatestPath := A_LoopFileFullPath
            LatestTime := A_LoopFileTimeModified
        }
    }

    return LatestPath
}

OpenFileDialogRobust(BrowserHwnd, AttachPointX, AttachPointY, FileItemX, FileItemY)
{
    global FileMenuClicked

    ExistingDialogs := SnapshotDialogWindows()

    ; SIM3_UPLOAD_MENU_KEYBOARD_ONLY_V3_1
    ; Never click a ChatGPT menu row by guessed screen coordinates.
    ; The file-upload entry is selected only by keyboard navigation.
    ; If the file dialog does not open, fail closed.

    WriteStatus("FILE_MENU", "KEYBOARD_END_ENTER")
    SendEvent "{End}"
    Sleep 350
    SendEvent "{Enter}"
    FileMenuClicked := true

    DialogHwnd := WaitForNewFileDialog(BrowserHwnd, ExistingDialogs, 5)
    if DialogHwnd
        return DialogHwnd

    SendEvent "{Esc}"
    Sleep 350
    MouseMove AttachPointX, AttachPointY, 10
    Click AttachPointX, AttachPointY
    Sleep 750
    ExistingDialogs := SnapshotDialogWindows()

    WriteStatus("FILE_MENU", "KEYBOARD_UP_ENTER")
    SendEvent "{Up}"
    Sleep 350
    SendEvent "{Enter}"
    FileMenuClicked := true

    DialogHwnd := WaitForNewFileDialog(BrowserHwnd, ExistingDialogs, 5)
    if DialogHwnd
        return DialogHwnd

    if PointInsideBrowser(FileItemX, FileItemY, BrowserHwnd)
    {
        SendEvent "{Esc}"
        Sleep 300
        MouseMove AttachPointX, AttachPointY, 10
        Click AttachPointX, AttachPointY
        Sleep 750
        ExistingDialogs := SnapshotDialogWindows()
        WriteStatus("FILE_MENU", "FIXED_FILE_ITEM_COORDINATE_FALLBACK")
        MouseMove FileItemX, FileItemY, 10
        Click FileItemX, FileItemY
        FileMenuClicked := true
        DialogHwnd := WaitForNewFileDialog(BrowserHwnd, ExistingDialogs, 6)
        if DialogHwnd
            return DialogHwnd
    }

    WriteStatus("FILE_MENU", "ALL_FILE_MENU_METHODS_FAILED")
    return 0
}
SnapshotDialogWindows()
{
    Existing := Map()
    try
    {
        for Hwnd in WinGetList("ahk_class #32770")
            Existing[Hwnd] := true
    }
    return Existing
}

WaitForNewFileDialog(BrowserHwnd, ExistingDialogs, TimeoutSeconds)
{
    BrowserProcess := ""
    try BrowserProcess := WinGetProcessName("ahk_id " BrowserHwnd)

    StartTick := A_TickCount
    Deadline := StartTick + Floor(TimeoutSeconds * 1000)

    while (A_TickCount < Deadline)
    {
        FallbackHwnd := 0
        try
        {
            for Hwnd in WinGetList("ahk_class #32770")
            {
                if ExistingDialogs.Has(Hwnd)
                    continue

                if !FallbackHwnd
                    FallbackHwnd := Hwnd

                DialogProcess := ""
                try DialogProcess := WinGetProcessName("ahk_id " Hwnd)

                if (BrowserProcess = "") || (DialogProcess = BrowserProcess) || (DialogProcess = "explorer.exe")
                    return Hwnd
            }
        }

        ; If Chromium delegates the dialog to a process name not known here,
        ; accept only a newly-created #32770 after one second. Existing dialogs
        ; were snapshotted before the upload command, so this remains fail-safe.
        if FallbackHwnd && ((A_TickCount - StartTick) >= 1000)
            return FallbackHwnd

        Sleep 100
    }

    return 0
}

SetFileDialogPathRobust(DialogHwnd, SourcePath)
{
    Result := Map(
        "ok", false,
        "dialog_closed", false,
        "method", "NONE",
        "controls", "NONE"
    )

    ControlsSummary := []

    ; First try the classic common-dialog filename edit control.
    try
    {
        ControlFocus "Edit1", "ahk_id " DialogHwnd
        ControlSetText SourcePath, "Edit1", "ahk_id " DialogHwnd
        Sleep 150
        ReadBack := ControlGetText("Edit1", "ahk_id " DialogHwnd)
        ControlsSummary.Push("EDIT1")
        if (Trim(ReadBack, Chr(34)) = SourcePath)
        {
            Result["ok"] := true
            Result["method"] := "CONTROL_EDIT1"
            Result["controls"] := JoinText(ControlsSummary, ",")
            return Result
        }
    }
    catch
    {
        ControlsSummary.Push("EDIT1_FAILED")
    }

    ; Windows 11 and Chromium updates may expose a different Edit control.
    ; Select the lowest visible/enabled edit control, which is normally the
    ; file-name field, and verify the value by reading it back.
    Candidates := []
    try
    {
        for CtrlHwnd in WinGetControlsHwnd("ahk_id " DialogHwnd)
        {
            ClassName := ""
            try ClassName := WinGetClass("ahk_id " CtrlHwnd)
            if !InStr(ClassName, "Edit")
                continue

            X := 0, Y := 0, W := 0, H := 0
            try
            {
                ControlGetPos &X, &Y, &W, &H, CtrlHwnd
            }
            catch
            {
                continue
            }

            Visible := true
            Enabled := true
            try
            {
                Visible := ControlGetVisible(CtrlHwnd)
            }
            try
            {
                Enabled := ControlGetEnabled(CtrlHwnd)
            }

            ControlsSummary.Push(ClassName "@" Y "x" W)
            if Visible && Enabled && (W >= 120) && (H >= 15)
                Candidates.Push(Map("hwnd", CtrlHwnd, "y", Y, "w", W))
        }
    }

    ; Manual descending sort by vertical position avoids dependency on locale
    ; or a fixed ClassNN such as Edit1/Edit2.
    Loop Candidates.Length
    {
        BestIndex := A_Index
        Inner := A_Index + 1
        while (Inner <= Candidates.Length)
        {
            if (Candidates[Inner]["y"] > Candidates[BestIndex]["y"])
                BestIndex := Inner
            Inner += 1
        }
        if (BestIndex != A_Index)
        {
            Temp := Candidates[A_Index]
            Candidates[A_Index] := Candidates[BestIndex]
            Candidates[BestIndex] := Temp
        }
    }

    for Candidate in Candidates
    {
        CtrlHwnd := Candidate["hwnd"]
        try
        {
            ControlFocus CtrlHwnd
            ControlSetText SourcePath, CtrlHwnd
            Sleep 150
            ReadBack := ControlGetText(CtrlHwnd)
            if (Trim(ReadBack, Chr(34)) = SourcePath)
            {
                Result["ok"] := true
                Result["method"] := "ENUMERATED_EDIT_CONTROL"
                Result["controls"] := JoinText(ControlsSummary, ",")
                return Result
            }
        }
    }

    ; Locale-neutral keyboard fallback. Ctrl+L focuses the common-dialog
    ; location field on current Windows builds. Supplying a full file path and
    ; pressing Enter opens the file directly without relying on a translated
    ; "File name" access key.
    try
    {
        WinActivate "ahk_id " DialogHwnd
        if WinWaitActive("ahk_id " DialogHwnd, , 3)
        {
            ClipboardBackup := ClipboardAll()
            A_Clipboard := SourcePath
            SendEvent "^l"
            Sleep 250
            SendEvent "^v"
            Sleep 250
            SendEvent "{Enter}"
            Sleep 200
            A_Clipboard := ClipboardBackup

            if WinWaitClose("ahk_id " DialogHwnd, , 15)
            {
                Result["ok"] := true
                Result["dialog_closed"] := true
                Result["method"] := "KEYBOARD_CTRL_L_FULL_PATH_ENTER"
                Result["controls"] := JoinText(ControlsSummary, ",")
                return Result
            }
        }
    }
    catch
    {
    }

    Result["controls"] := JoinText(ControlsSummary, ",")
    return Result
}

JoinText(Items, Separator)
{
    Text := ""
    for Index, Item in Items
    {
        if (Index > 1)
            Text .= Separator
        Text .= Item
    }
    return Text = "" ? "NONE" : Text
}

WaitForAttachmentReady(BrowserHwnd)
{
    global AttachmentReadyPollCount, AttachmentStablePollCount
    global SourceReport

    ; SIM3_ATTACHMENT_FOCUS_REFRESH_FALLBACK_V2
    ; The ChatGPT composer can remain visually ready while stale pixel/template
    ; checks keep returning false. Reactivate the browser and refocus the
    ; composer during the bounded wait. For small text reports, permit a
    ; conservative time-based fallback only after the native readiness checks
    ; and at least two focus refreshes have had time to run.
    WaitStarted := A_TickCount
    Deadline := WaitStarted + 45000
    StableReadyCount := 0
    FocusRefreshCount := 0
    ReportSize := 0

    try ReportSize := FileGetSize(SourceReport)

    FallbackDelayMs := 12000
    if (ReportSize > (5 * 1024 * 1024))
        FallbackDelayMs := 30000
    else if (ReportSize > (1024 * 1024))
        FallbackDelayMs := 20000

    while (A_TickCount < Deadline)
    {
        AttachmentReadyPollCount += 1

        if !WinExist("ahk_id " BrowserHwnd)
            return false

        ; Dosya penceresinin kapandığı ana akışta zaten doğrulanıyor.
        ; Sistem genelindeki ilgisiz #32770 pencereleri teslimatı engellememeli.

        WinActivate "ahk_id " BrowserHwnd
        WinWaitActive "ahk_id " BrowserHwnd, , 1

        if (Mod(AttachmentReadyPollCount, 2) = 0)
        {
            WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
            ComposerPointX := ClientX + Floor(ClientW * 0.56)
            ComposerPointY := ClientY + ClientH - 55
            if PointInsideBrowser(ComposerPointX, ComposerPointY, BrowserHwnd)
            {
                MouseMove ComposerPointX, ComposerPointY, 10
                Click ComposerPointX, ComposerPointY
                FocusRefreshCount += 1
                Sleep 350
            }
        }

        IconReady := FindReportDocumentIcon(BrowserHwnd)
        SendReady := IsConfiguredSendButtonReady(BrowserHwnd)
        FocusFallbackReady := (
            ((A_TickCount - WaitStarted) >= FallbackDelayMs)
            && (FocusRefreshCount >= 2)
            && WinActive("ahk_id " BrowserHwnd)
        )

        if (IconReady || SendReady || FocusFallbackReady)
            StableReadyCount += 1
        else
            StableReadyCount := 0

        AttachmentStablePollCount := StableReadyCount

        if (StableReadyCount >= 2)
            return true

        Sleep 750
    }

    return false
}

IsConfiguredSendButtonReady(BrowserHwnd)
{
    global SendX, SendY

    if !PointInsideBrowser(SendX, SendY, BrowserHwnd)
        return false

    ; SIM3_THEME_NEUTRAL_SEND_BUTTON_READY_V5
    ; Enabled send buttons are dark on light themes and bright on dark themes.
    ; Compare the button body with its surrounding background instead of relying
    ; on one absolute dark-colour threshold.

    InsideOffsets := [
        [-9, 0],
        [9, 0],
        [0, -9],
        [0, 9],
        [-6, -6],
        [6, -6],
        [-6, 6],
        [6, 6]
    ]

    OutsideOffsets := [
        [-24, 0],
        [24, 0],
        [0, -24],
        [0, 24],
        [-17, -17],
        [17, -17],
        [-17, 17],
        [17, 17]
    ]

    InsideTotal := 0
    OutsideTotal := 0
    InsideCount := 0
    OutsideCount := 0
    DarkCount := 0
    BrightCount := 0

    for Offset in InsideOffsets
    {
        try
            Color := PixelGetColor(SendX + Offset[1], SendY + Offset[2], "RGB")
        catch
            continue

        Red := (Color >> 16) & 0xFF
        Green := (Color >> 8) & 0xFF
        Blue := Color & 0xFF
        Luma := Floor((Red * 299 + Green * 587 + Blue * 114) / 1000)

        InsideTotal += Luma
        InsideCount += 1

        if (Luma < 105)
            DarkCount += 1

        if (Luma > 185)
            BrightCount += 1
    }

    for Offset in OutsideOffsets
    {
        try
            Color := PixelGetColor(SendX + Offset[1], SendY + Offset[2], "RGB")
        catch
            continue

        Red := (Color >> 16) & 0xFF
        Green := (Color >> 8) & 0xFF
        Blue := Color & 0xFF
        Luma := Floor((Red * 299 + Green * 587 + Blue * 114) / 1000)

        OutsideTotal += Luma
        OutsideCount += 1
    }

    if (InsideCount < 5) || (OutsideCount < 5)
        return false

    InsideMean := InsideTotal / InsideCount
    OutsideMean := OutsideTotal / OutsideCount
    Contrast := Abs(InsideMean - OutsideMean)

    if (DarkCount >= 5)
        return true

    if (BrightCount >= 5) && (Contrast >= 45)
        return true

    return Contrast >= 60
}
SendAttachedReportByKeyboard(BrowserHwnd)
{
    global SendX, SendY

    ; SIM3_DIRECT_SEND_BUTTON_CLICK_V1
    ; The previous implementation focused the composer and pressed Enter.
    ; Attachment-only messages may ignore Enter even when the visible send
    ; button is enabled. Click the configured send-button position directly.

    if !WinExist("ahk_id " BrowserHwnd)
        return false

    WinActivate "ahk_id " BrowserHwnd
    WinWaitActive "ahk_id " BrowserHwnd, , 2

    if !WinActive("ahk_id " BrowserHwnd)
        return false

    Sleep 500

    TargetX := SendX
    TargetY := SendY

    if !PointInsideBrowser(TargetX, TargetY, BrowserHwnd)
    {
        try
        {
            WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd

            ; ChatGPT composer is centered and has a bounded maximum width.
            ; This is used only when the configured point is outside the browser.
            TargetX := ClientX + Floor(ClientW / 2) + 330
            TargetY := ClientY + ClientH - 64
        }
        catch
        {
            return false
        }
    }

    if !PointInsideBrowser(TargetX, TargetY, BrowserHwnd)
        return false

    MouseMove TargetX, TargetY, 10
    Sleep 300
    Click TargetX, TargetY
    Sleep 1500

    return true
}

FindReportDocumentIcon(BrowserHwnd)
{
    global ReportDocumentTemplate, DocumentSearchCount

    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return false

    SearchLeft := ClientX + Floor(ClientW * 0.12)
    SearchRight := ClientX + Floor(ClientW * 0.92)
    SearchTop := ClientY + Floor(ClientH * 0.55)
    SearchBottom := ClientY + ClientH - 70

    FoundX := 0
    FoundY := 0
    DocumentSearchCount += 1

    try
        return ImageSearch(&FoundX, &FoundY, SearchLeft, SearchTop, SearchRight, SearchBottom, "*90 *TransWhite " ReportDocumentTemplate)
    catch
        return false
}

FindPlusIcon(BrowserHwnd, &AttachPointX, &AttachPointY)
{
    global PlusIconTemplate, PlusSearchCount, PlusFoundCount

    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return false

    SearchLeft := ClientX + Floor(ClientW * 0.05)
    SearchRight := ClientX + Floor(ClientW * 0.40)
    SearchTop := ClientY + Floor(ClientH * 0.65)
    SearchBottom := ClientY + ClientH - 25

    FoundX := 0
    FoundY := 0
    PlusSearchCount += 1

    try
        Found := ImageSearch(&FoundX, &FoundY, SearchLeft, SearchTop, SearchRight, SearchBottom, "*90 *TransWhite " PlusIconTemplate)
    catch
        return false

    if !Found
        return false

    PlusFoundCount += 1
    AttachPointX := FoundX + 16
    AttachPointY := FoundY + 16
    return true
}

ScrollToBottom(BrowserHwnd)
{
    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return

    X := ClientX + Floor(ClientW * 0.78)
    Y := ClientY + Floor(ClientH * 0.55)

    MouseMove X, Y, 8
    Click X, Y
    Sleep 150

    SendEvent "^{End}"
    Sleep 350
    SendEvent "{End}"
    Sleep 180
    Loop 8
    {
        SendEvent "{WheelDown}"
        Sleep 70
    }
}

FindBrowserWindow()
{
    Active := WinExist("A")

    if Active
    {
        try
        {
            Process := WinGetProcessName("ahk_id " Active)
            Title := WinGetTitle("ahk_id " Active)

            if ((Process = "chrome.exe") || (Process = "msedge.exe")) && (InStr(Title, "ChatGPT") || InStr(Title, "SIM3"))
                return Active
        }
    }

    Candidates := []

    for Hwnd in WinGetList("ahk_exe chrome.exe")
        Candidates.Push(Hwnd)

    for Hwnd in WinGetList("ahk_exe msedge.exe")
        Candidates.Push(Hwnd)

    for Hwnd in Candidates
    {
        Title := WinGetTitle("ahk_id " Hwnd)

        if InStr(Title, "ChatGPT") || InStr(Title, "SIM3")
            return Hwnd
    }

    return 0
}

PointInsideBrowser(X, Y, BrowserHwnd)
{
    if (X < 0) || (Y < 0)
        return false

    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return false

    return (X >= ClientX) && (X <= ClientX + ClientW) && (Y >= ClientY) && (Y <= ClientY + ClientH)
}

WriteStatus(Status, Reason)
{
    global ResultPath, StartedAt, StartTick, BrowserHwndUsed, BrowserTitleUsed, SourceReport, SourceReportSelection, DeliveryRunToken
    global AttachMode, AttachClicked, FileMenuClicked, FileDialogOpened, FilePathSet, FileDialogClosed
    global FilePathSetMethod, FileDialogTitle, FileDialogProcess, FileDialogControlSummary
    global AttachmentReady, AttachmentReadyPollCount, AttachmentStablePollCount, SendClicked, SendClickMode
    global PlusSearchCount, PlusFoundCount, DocumentSearchCount, DocumentFoundCount, LastState

    Elapsed := Floor((A_TickCount - StartTick) / 1000)

    Text := ""
    Text .= "STEP=SIM3_V4_1_REPORT_DELIVERY`r`n"
    Text .= "METHOD=V4_7_UNIFIED_TOKEN_OWNED_RETRY_SAFE`r`n"
    Text .= "RUN_TOKEN=" DeliveryRunToken "`r`n"
    Text .= "STARTED_AT=" StartedAt "`r`n"
    Text .= "UPDATED_AT=" A_Now "`r`n"
    Text .= "ELAPSED_SECONDS=" Elapsed "`r`n"
    Text .= "SOURCE_REPORT=" SourceReport "`r`n"
    Text .= "SOURCE_REPORT_SELECTION=" SourceReportSelection "`r`n"
    Text .= "BROWSER_TITLE_USED=" BrowserTitleUsed "`r`n"
    Text .= "BROWSER_HWND_USED=" BrowserHwndUsed "`r`n"
    Text .= "ATTACH_MODE=" AttachMode "`r`n"
    Text .= "ATTACH_CLICKED=" BoolText(AttachClicked) "`r`n"
    Text .= "FILE_MENU_CLICKED=" BoolText(FileMenuClicked) "`r`n"
    Text .= "FILE_DIALOG_OPENED=" BoolText(FileDialogOpened) "`r`n"
    Text .= "FILE_PATH_SET=" BoolText(FilePathSet) "`r`n"
    Text .= "FILE_PATH_SET_METHOD=" FilePathSetMethod "`r`n"
    Text .= "FILE_DIALOG_TITLE=" FileDialogTitle "`r`n"
    Text .= "FILE_DIALOG_PROCESS=" FileDialogProcess "`r`n"
    Text .= "FILE_DIALOG_CONTROL_SUMMARY=" FileDialogControlSummary "`r`n"
    Text .= "FILE_DIALOG_CLOSED=" BoolText(FileDialogClosed) "`r`n"
    Text .= "ATTACHMENT_READY=" BoolText(AttachmentReady) "`r`n"
    Text .= "ATTACHMENT_READY_POLL_COUNT=" AttachmentReadyPollCount "`r`n"
    Text .= "ATTACHMENT_STABLE_POLL_COUNT=" AttachmentStablePollCount "`r`n"
    Text .= "SEND_CLICKED=" BoolText(SendClicked) "`r`n"
    Text .= "SEND_MODE=" SendClickMode "`r`n"
    Text .= "PLUS_SEARCH_COUNT=" PlusSearchCount "`r`n"
    Text .= "PLUS_FOUND_COUNT=" PlusFoundCount "`r`n"
    Text .= "DOCUMENT_SEARCH_COUNT=" DocumentSearchCount "`r`n"
    Text .= "DOCUMENT_FOUND_COUNT=" DocumentFoundCount "`r`n"
    Text .= "LAST_STATE=" LastState "`r`n"
    Text .= "RESULT_REASON=" Reason "`r`n"
    Text .= "FINAL_STATUS=" Status "`r`n"

    AtomicWrite(ResultPath, Text)
}

Finish(Status, Reason, ExitCode)
{
    global LastState

    LastState := Reason
    WriteStatus(Status, Reason)



    ExitApp ExitCode
}

AtomicWrite(Path, Text, RetryCount := 40, RetrySleepMs := 125)
{
    SplitPath Path, , &Dir
    if !DirExist(Dir)
        DirCreate Dir

    Temp := Path ".sim3tmp." DllCall("GetCurrentProcessId", "UInt") "." A_TickCount

    Loop RetryCount
    {
        try
        {
            if FileExist(Temp)
                FileDelete Temp
            FileAppend Text, Temp, "UTF-8"
            FileMove Temp, Path, 1
            return true
        }
        catch as Err
        {
            try
            {
                if FileExist(Temp)
                    FileDelete Temp
            }
            if (A_Index >= RetryCount)
                throw Error("ATOMIC_WRITE_FAILED: " Path " | " Err.Message)
            Sleep RetrySleepMs
        }
    }

    return false
}

BoolText(Value)
{
    return Value ? "True" : "False"
}

EmergencyStop(*)
{
    global Root
    try
    {
        PausePath := Root "\PAUSE.flag"
        if FileExist(PausePath)
            FileDelete PausePath
        FileAppend "USER_EMERGENCY_STOP", PausePath, "UTF-8"
    }
    Finish("PAUSED", "USER_EMERGENCY_STOP", 20)
}
; >>> SIM3_UNIFIED_ERROR_HANDLER >>>
SIM3_FullFixUnhandledErrorV3(Err, Mode) {
    global LastState
    try {
        RootDir := RegExReplace(A_ScriptDir, "\\[^\\]+$")
        DirCreate(RootDir "\LOGS")
        Line := FormatTime(A_Now, "yyyyMMddHHmmss")
            . " | SCRIPT=" A_ScriptName
            . " | MESSAGE=" Err.Message
            . " | WHAT=" Err.What
            . " | LINE=" Err.Line
            . "`n"
        FileAppend(Line, RootDir "\LOGS\SIM3_AHK_RUNTIME_ERRORS.log", "UTF-8")
        LastState := "AHK_RUNTIME_ERROR"
        WriteStatus("FAILED", "AHK_RUNTIME_ERROR")
    }
    ExitApp(90)
    return 1
}
; <<< SIM3_UNIFIED_ERROR_HANDLER <<<
