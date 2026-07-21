#Requires AutoHotkey v2.0
#SingleInstance Force
#ErrorStdOut
OnError(SIM3_FullFixUnhandledErrorV3)
CoordMode "Mouse", "Screen"
CoordMode "Pixel", "Screen"
SetTitleMatchMode 2

global Root := A_Args.Length >= 1 ? RTrim(A_Args[1], "\/") : A_ScriptDir "\.."
global TaskPath := Root "\INBOX\TASK.txt"
global CaptureDir := Root "\CAPTURE"
global ResultPath := CaptureDir "\LAST_CAPTURE_RESULT.txt"
global CaptureTokenPath := CaptureDir "\CURRENT_CAPTURE_TOKEN.txt"
global LastPanelPath := CaptureDir "\LAST_CAPTURED_PANEL.txt"
global LastTaskPath := CaptureDir "\LAST_CAPTURED_TASK.txt"
global LastInvalidClipboardPath := CaptureDir "\LAST_INVALID_CLIPBOARD.txt"
global LastInvalidPanelPath := CaptureDir "\LAST_INVALID_PANEL.txt"
global CopyTemplate := CaptureDir "\SIM3_CHATGPT_COPY_ICON_TEMPLATE.png"
global RunCmd := Root "\SIM3_V3_RUN_TASK_NO_PAUSE.cmd"
global ReportsDir := Root "\REPORTS"
global ReportPath := ""

global CaptureRunToken := ReadCaptureRunToken()
global OwnerPid := DllCall("GetCurrentProcessId", "UInt")
global StartedAt := A_Now
global StartTick := A_TickCount
global PollCount := 0
global CopySearchCount := 0
global CopyFoundCount := 0
global CopyAttemptCount := 0
global ClipboardLength := 0
global InvalidClipboardCount := 0
global DuplicateCount := 0
global LastState := "INITIALIZING"
global LastSource := ""
global LastInvalidReason := "NONE"
global BrowserTitleUsed := ""
global BrowserHwndUsed := 0
global Completed := false
global CaptureInProgress := false
global MaxWaitMs := 300000
global InitialRenderSettleMs := 700
global FastPollWindowMs := 30000
global FastPollMs := 900
global NormalPollMs := 2500

Hotkey "^!x", EmergencyStop
Hotkey "^!c", ClickCurrentMouseAndCapture
Hotkey "^!r", ResetDuplicateGuard

if !DirExist(CaptureDir)
    DirCreate CaptureDir

if !FileExist(CopyTemplate)
    Finish("FAILED", "COPY_ICON_TEMPLATE_NOT_FOUND", 50)

if !FileExist(RunCmd)
    Finish("FAILED", "RUNNER_CMD_NOT_FOUND", 51)

if (CaptureRunToken = "")
    Finish("FAILED", "CAPTURE_RUN_TOKEN_NOT_FOUND", 54)

OnClipboardChange ClipboardChanged

BrowserHwnd := FindBrowserWindow()
if !BrowserHwnd
    Finish("FAILED", "CHATGPT_BROWSER_WINDOW_NOT_FOUND", 52)

BrowserHwndUsed := BrowserHwnd
BrowserTitleUsed := WinGetTitle("ahk_id " BrowserHwnd)
LastState := "ARMED_WAITING_FOR_WHITE_PANEL"
WriteStatus("ARMED", LastState)
Sleep InitialRenderSettleMs

; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V3.5", "Beyaz panel görev yakalama etkin. Gerekirse mesajın altındaki Copy düğmesine bir kez tıkla.", 5
; SIM3_UI_SILENT_DISABLED: ToolTip "SIM3 V3.5 beyaz panel yakalama etkin`nDurdur: Ctrl+Alt+X`nElle Copy: Ctrl+Alt+C"
; SIM3_UI_SILENT_DISABLED: SetTimer HideToolTip, -7000

Loop
{
    if Completed
        break

    if ((A_TickCount - StartTick) >= MaxWaitMs)
        Finish("PAUSED", "WHITE_PANEL_NOT_READY_300_SECONDS", 20)

    PollCount += 1

    WinActivate "ahk_id " BrowserHwnd

    if !WinWaitActive("ahk_id " BrowserHwnd, , 5)
    {
        LastState := "BROWSER_NOT_ACTIVE"
        WriteStatus("ARMED", LastState)
        Sleep CurrentPollMs()
        continue
    }

    ScrollToLatest(BrowserHwnd)
    Sleep 450
    ScrollToLatest(BrowserHwnd)
    Sleep 350

    Candidates := FindCopyCandidates(BrowserHwnd)

    if (Candidates.Length = 0)
    {
        LastState := "NO_COPY_ICON_CANDIDATE"
        WriteStatus("ARMED", LastState)
        Sleep CurrentPollMs()
        continue
    }

    while Candidates.Length > 0
    {
        Point := PopBottomCandidate(Candidates)

        if ClickCopyAndAccept(Point.X, Point.Y, "AUTO_WHITE_PANEL_COPY")
            break
    }

    if Completed
        break

    LastState := "COPY_CANDIDATES_FOUND_BUT_NO_VALID_PANEL"
    WriteStatus("ARMED", LastState)
    Sleep CurrentPollMs()
}

ClipboardChanged(DataType)
{
    global Completed, CaptureInProgress

    if Completed || CaptureInProgress
        return

    if (DataType != 1)
        return

    Text := A_Clipboard
    if (StrLen(Text) < 80)
        return

    TryAcceptClipboard(Text, "CLIPBOARD_WATCH")
}

ClickCurrentMouseAndCapture(*)
{
    global Completed, CaptureInProgress

    if Completed || CaptureInProgress
        return

    MouseGetPos &X, &Y
    ClickCopyAndAccept(X, Y, "HOTKEY_CURRENT_MOUSE")
}

ResetDuplicateGuard(*)
{
    global LastPanelPath, LastTaskPath, DuplicateCount, LastState

    if FileExist(LastPanelPath)
        FileDelete LastPanelPath

    if FileExist(LastTaskPath)
        FileDelete LastTaskPath

    DuplicateCount := 0
    LastState := "DUPLICATE_GUARD_RESET"
    WriteStatus("ARMED", LastState)
    ; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V3.5", "Aynı görev koruması temizlendi.", 4
}

ScrollToLatest(BrowserHwnd)
{
    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return

    X := ClientX + Floor(ClientW * 0.78)
    Y := ClientY + Floor(ClientH * 0.55)

    MouseMove X, Y, 10
    Click X, Y
    Sleep 200

    ; V4.7R1: Down_20 was not reliable in long conversations.
    ; Ctrl+End + End + WheelDown forces the viewport toward the newest assistant message.
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

CurrentPollMs()
{
    global StartTick, FastPollWindowMs, FastPollMs, NormalPollMs

    if ((A_TickCount - StartTick) <= FastPollWindowMs)
        return FastPollMs

    return NormalPollMs
}

ReadCaptureRunToken()
{
    global CaptureTokenPath

    if !FileExist(CaptureTokenPath)
        return ""

    try
        return Trim(FileRead(CaptureTokenPath, "UTF-8"), " `t`r`n")
    catch
        return ""
}

FindCopyCandidates(BrowserHwnd)
{
    global CopyTemplate, CopySearchCount, CopyFoundCount

    Candidates := []

    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return Candidates

    SearchLeft := ClientX + Floor(ClientW * 0.08)
    SearchRight := ClientX + Floor(ClientW * 0.97)
    ; V4.7R1: after forcing bottom, prefer lower/newer visible copy icons.
    SearchTop := ClientY + Floor(ClientH * 0.14)
    SearchBottom := ClientY + ClientH - 35

    CurrentTop := SearchTop

    Loop 100
    {
        FoundX := 0
        FoundY := 0
        CopySearchCount += 1

        try
            Found := ImageSearch(
                &FoundX,
                &FoundY,
                SearchLeft,
                CurrentTop,
                SearchRight,
                SearchBottom,
                "*90 *TransWhite " CopyTemplate
            )
        catch
            break

        if !Found
            break

        CopyFoundCount += 1
        AddUniqueCandidate(Candidates, FoundX + 20, FoundY + 19)
        CurrentTop := FoundY + 5

        if (CurrentTop >= SearchBottom)
            break
    }

    return Candidates
}

AddUniqueCandidate(Candidates, X, Y)
{
    for Item in Candidates
    {
        if (Abs(Item.X - X) <= 10) && (Abs(Item.Y - Y) <= 10)
            return
    }

    Candidates.Push({X: X, Y: Y})
}

PopBottomCandidate(Candidates)
{
    BestIndex := 1
    BestY := Candidates[1].Y

    Loop Candidates.Length
    {
        Index := A_Index

        if (Candidates[Index].Y > BestY)
        {
            BestIndex := Index
            BestY := Candidates[Index].Y
        }
    }

    return Candidates.RemoveAt(BestIndex)
}

ClickCopyAndAccept(X, Y, Source)
{
    global CaptureInProgress, CopyAttemptCount, ClipboardLength
    global InvalidClipboardCount

    if CaptureInProgress
        return false

    CaptureInProgress := true
    A_Clipboard := ""

    MouseMove X, Y, 12
    Sleep 350
    Click X, Y
    CopyAttemptCount += 1

    if !ClipWait(5)
    {
        CaptureInProgress := false
        return false
    }

    Candidate := A_Clipboard
    ClipboardLength := StrLen(Candidate)
    Accepted := TryAcceptClipboard(Candidate, Source)

    if !Accepted
        InvalidClipboardCount += 1

    CaptureInProgress := false
    return Accepted
}

TryAcceptClipboard(Text, Source)
{
    global Completed, DuplicateCount, LastState, LastSource
    global LastPanelPath, LastTaskPath, TaskPath, RunCmd, Root, ReportPath

    Panel := ExtractBoundedPanel(Text)

    if (Panel = "")
    {
        if IsTerminalAssistantResponse(Text)
        {
            Completed := true
            LastSource := Source
            LastState := "NO_NEXT_COMMAND_TERMINAL_RESPONSE"
            WriteStatus("NO_NEXT_COMMAND", "NO_COMPLETE_SIM3_COMMAND_MANUAL_GATE_DETECTED")
            ; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V4.7R2", "Yeni SIM3 komutu yok. Manuel kapı algılandı; otomasyon duruyor.", 5
            return true
        }

        SaveInvalidClipboard(Text, "NO_COMPLETE_SIM3_AGENT_COMMAND_BLOCK")
        LastState := "INVALID_CLIPBOARD_NO_COMPLETE_BLOCK"
        WriteStatus("ARMED", LastState)
        return false
    }

    if !ValidatePanel(Panel, &Reason)
    {
        SaveInvalidClipboard(Text, "INVALID_PANEL_" Reason)
        SaveInvalidPanel(Panel)
        LastState := "INVALID_PANEL_" Reason
        WriteStatus("ARMED", LastState)
        return false
    }

    Task := BuildWorkerTask(Panel)

    if (Task = "")
    {
        LastState := "TASK_EXTRACTION_FAILED"
        WriteStatus("ARMED", LastState)
        return false
    }

    if FileExist(LastTaskPath)
    {
        Existing := FileRead(LastTaskPath, "UTF-8")

        if (Normalize(Existing) = Normalize(Task))
        {
            DuplicateCount += 1
            LastState := "DUPLICATE_TASK_IGNORED"
            WriteStatus("ARMED", LastState)
            return false
        }
    }

    AtomicWrite(LastPanelPath, Panel "`n")
    AtomicWrite(LastTaskPath, Task "`n")
    AtomicWrite(TaskPath, Task "`n")

    Completed := true
    LastSource := Source
    LastState := "WHITE_PANEL_CAPTURED"
    WriteStatus("CAPTURED", "TASK_CAPTURED_AND_RUNNER_STARTING")
    ; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V3.5", "Beyaz panel yakalandı. Codex çalıştırılıyor.", 4

    Q := Chr(34)
    Command := A_ComSpec " /d /s /c " Q Q RunCmd Q " " Q TaskPath Q Q
    ExitCode := -1

    try
        ExitCode := RunWait(Command, Root, "Hide")
    catch as Err
    {
        LastState := "RUNNER_START_FAILED"
        WriteStatus("FAILED", LastState)
        ; SIM3_FIXED_SILENT_UI: MsgBox "Görev yakalandı fakat runner başlatılamadı.`n" Err.Message, "SIM3 V3.5", 16
        ExitApp 53
    }

    if (ExitCode = 0)
    {
        ReportPath := ReadLatestReadyReportPath()
        LastState := "RUNNER_COMPLETED"
        WriteStatus("OK", "TASK_CAPTURED_AND_RUNNER_COMPLETED")
        ; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V4.3", "Codex tamamlandı. Loop controller delivery adımına geçecek.", 3
        ExitApp 0
    }

    LastState := "RUNNER_EXIT_CODE_" ExitCode
    WriteStatus("FAILED", LastState)
    ; SIM3_UI_SILENT_DISABLED: TrayTip "SIM3 V4.3", "Codex runner hata ile tamamlandı. EXIT_CODE=" ExitCode, 5
    ExitApp ExitCode
}

ExtractBoundedPanel(Text)
{
    Normalized := Normalize(Text)
    Header := "# SIM3_AGENT_COMMAND"
    Footer := "# END_SIM3_AGENT_COMMAND"

    ; V4.7R1: A copied assistant message may contain prose plus a command,
    ; or in rare cases multiple historical command blocks. Use the last complete block.
    StartPos := FindLastOccurrence(Normalized, Header)

    if (StartPos <= 0)
        return ""

    EndPos := InStr(Normalized, Footer, true, StartPos + StrLen(Header))

    if (EndPos <= StartPos)
        return ""

    BlockEnd := EndPos + StrLen(Footer) - 1
    return Trim(SubStr(Normalized, StartPos, BlockEnd - StartPos + 1), " `t`n")
}

ValidatePanel(Panel, &Reason)
{
    Reason := ""

    if !HasExactLine(Panel, "# SIM3_AGENT_COMMAND")
    {
        Reason := "HEADER"
        return false
    }

    if !HasExactLine(Panel, "# END_SIM3_AGENT_COMMAND")
    {
        Reason := "FOOTER"
        return false
    }

    if !HasExactLine(Panel, "# PROTOCOL=SIM3_AUTOMATION_V1")
    {
        Reason := "PROTOCOL"
        return false
    }

    if (GetHeaderValue(Panel, "# AUTOMATION_ACTION") != "EXECUTE_TASK")
    {
        Reason := "ACTION"
        return false
    }

    TaskId := GetHeaderValue(Panel, "# TASK_ID")
    Mode := GetHeaderValue(Panel, "# MODE")
    ReportFilename := GetHeaderValue(Panel, "# REPORT_FILENAME")

    if !RegExMatch(TaskId, "^[A-Za-z0-9_.-]{4,160}$")
    {
        Reason := "TASK_ID"
        return false
    }

    if (Mode != "CODEX_READ_ONLY") && (Mode != "CODEX_WORKSPACE_WRITE")
    {
        Reason := "MODE"
        return false
    }

    if !RegExMatch(ReportFilename, "^[A-Za-z0-9_.-]+_FULL\.txt$")
    {
        Reason := "REPORT_FILENAME"
        return false
    }

    if (GetHeaderValue(Panel, "# CODEX_REQUIRED") != "True")
    {
        Reason := "CODEX_REQUIRED"
        return false
    }

    if (GetHeaderValue(Panel, "# WORKER_RUN_ALLOWED") != "True")
    {
        Reason := "WORKER_RUN_ALLOWED"
        return false
    }

    if (GetHeaderValue(Panel, "# CODEX_RUN_ALLOWED") != "True")
    {
        Reason := "CODEX_RUN_ALLOWED"
        return false
    }

    if !HasExactLine(Panel, "SIM3_AUTOMATION_TASK_BEGIN")
    {
        Reason := "TASK_BEGIN"
        return false
    }

    if !HasExactLine(Panel, "SIM3_AUTOMATION_TASK_END")
    {
        Reason := "TASK_END"
        return false
    }

    return true
}

BuildWorkerTask(Panel)
{
    TaskId := GetHeaderValue(Panel, "# TASK_ID")
    Mode := GetHeaderValue(Panel, "# MODE")
    ReportFilename := GetHeaderValue(Panel, "# REPORT_FILENAME")

    BeginMarker := "SIM3_AUTOMATION_TASK_BEGIN"
    EndMarker := "SIM3_AUTOMATION_TASK_END"

    BeginPos := InStr(Panel, BeginMarker, true)
    EndPos := InStr(Panel, EndMarker, true, BeginPos + StrLen(BeginMarker))

    if (BeginPos <= 0) || (EndPos <= BeginPos)
        return ""

    BodyStart := BeginPos + StrLen(BeginMarker)
    Body := Trim(SubStr(Panel, BodyStart, EndPos - BodyStart), " `t`n")

    if (StrLen(Body) < 80)
        return ""

    Task := ""
    Task .= "# TASK_ID=" TaskId "`n"
    Task .= "# MODE=" Mode "`n"
    Task .= "# REPORT_FILENAME=" ReportFilename "`n`n"
    Task .= Body
    return Task
}

ReadLatestReadyReportPath()
{
    global ReportsDir

    ReadyPath := ReportsDir "\LATEST_READY.json"
    if FileExist(ReadyPath)
    {
        try
        {
            Text := FileRead(ReadyPath, "UTF-8")
            if RegExMatch(Text, '"report_path"\s*:\s*"([^"]+)"', &M)
            {
                Candidate := StrReplace(M[1], "\\", "\")
                if FileExist(Candidate) && (FileGetSize(Candidate) > 0)
                    return Candidate
            }
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

WriteStatus(Status, Reason)
{
    global ResultPath, StartedAt, StartTick, PollCount
    global CopySearchCount, CopyFoundCount, CopyAttemptCount
    global ClipboardLength, InvalidClipboardCount, DuplicateCount
    global LastState, LastSource, LastInvalidReason, BrowserTitleUsed, BrowserHwndUsed
    global CaptureRunToken, OwnerPid, InitialRenderSettleMs, FastPollWindowMs, FastPollMs, NormalPollMs
    global ReportPath

    Elapsed := Floor((A_TickCount - StartTick) / 1000)
    Text := ""
    Text .= "STEP=SIM3_V3_5_WHITE_PANEL_CAPTURE`r`n"
    Text .= "METHOD=V4_7R3_TOKEN_OWNED_FAST_HANDOFF`r`n"
    Text .= "RUN_TOKEN=" CaptureRunToken "`r`n"
    Text .= "OWNER_PID=" OwnerPid "`r`n"
    Text .= "STARTED_AT=" StartedAt "`r`n"
    Text .= "UPDATED_AT=" A_Now "`r`n"
    Text .= "ELAPSED_SECONDS=" Elapsed "`r`n"
    Text .= "POLL_COUNT=" PollCount "`r`n"
    Text .= "COPY_SEARCH_COUNT=" CopySearchCount "`r`n"
    Text .= "COPY_FOUND_COUNT=" CopyFoundCount "`r`n"
    Text .= "COPY_ATTEMPT_COUNT=" CopyAttemptCount "`r`n"
    Text .= "CLIPBOARD_LENGTH=" ClipboardLength "`r`n"
    Text .= "INVALID_CLIPBOARD_COUNT=" InvalidClipboardCount "`r`n"
    Text .= "DUPLICATE_COUNT=" DuplicateCount "`r`n"
    Text .= "BROWSER_TITLE_USED=" BrowserTitleUsed "`r`n"
    Text .= "BROWSER_HWND_USED=" BrowserHwndUsed "`r`n"
    Text .= "CAPTURE_SOURCE=" LastSource "`r`n"
    Text .= "REPORT_PATH=" ReportPath "`r`n"
    Text .= "LAST_INVALID_REASON=" LastInvalidReason "`r`n"
    Text .= "LAST_STATE=" LastState "`r`n"
    Text .= "COPY_SELECTION_POLICY=LOWER_VISIBLE_BOTTOM_COPY_WITH_LAST_COMPLETE_BOUNDED_MARKER_EXTRACTION`r`n"
    Text .= "SCROLL_POLICY=DOUBLE_CTRL_END_END_WHEELDOWN_8`r`n"
    Text .= "INITIAL_RENDER_SETTLE_MS=" InitialRenderSettleMs "`r`n"
    Text .= "FAST_POLL_WINDOW_MS=" FastPollWindowMs "`r`n"
    Text .= "FAST_POLL_MS=" FastPollMs "`r`n"
    Text .= "NORMAL_POLL_MS=" NormalPollMs "`r`n"
    Text .= "INVALID_CAPTURE_DEBUG=LAST_INVALID_CLIPBOARD_AND_PANEL_ENABLED`r`n"
    Text .= "MAX_WAIT_SECONDS=300`r`n"
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

IsTerminalAssistantResponse(Text)
{
    Normalized := Normalize(Text)

    if InStr(Normalized, "# SIM3_AGENT_COMMAND")
        return false

    if InStr(Normalized, "WAVE4_SERVICE_ORCHESTRATION_STATUS=READY_FOR_MANUAL_REVIEW_AND_COMMIT")
        return true

    if InStr(Normalized, "READY_FOR_MANUAL_REVIEW_AND_COMMIT")
        return true

    if InStr(Normalized, "manuel review") && InStr(Normalized, "commit")
        return true

    if InStr(Normalized, "manual review") && InStr(Normalized, "commit")
        return true

    if InStr(Normalized, "commit/push kap")
        return true

    if InStr(Normalized, "doğru durma noktası") && InStr(Normalized, "commit")
        return true

    return false
}


SaveInvalidClipboard(Text, Reason)
{
    global LastInvalidClipboardPath, LastInvalidReason

    LastInvalidReason := Reason

    Header := ""
    Header .= "SIM3_INVALID_CAPTURE_DEBUG`r`n"
    Header .= "REASON=" Reason "`r`n"
    Header .= "CAPTURED_AT=" A_Now "`r`n"
    Header .= "CLIPBOARD_LENGTH=" StrLen(Text) "`r`n"
    Header .= "----- CLIPBOARD_BEGIN -----`r`n"

    AtomicWrite(LastInvalidClipboardPath, Header Text "`r`n----- CLIPBOARD_END -----`r`n")
}

SaveInvalidPanel(Panel)
{
    global LastInvalidPanelPath

    Header := ""
    Header .= "SIM3_INVALID_PANEL_DEBUG`r`n"
    Header .= "CAPTURED_AT=" A_Now "`r`n"
    Header .= "PANEL_LENGTH=" StrLen(Panel) "`r`n"
    Header .= "----- PANEL_BEGIN -----`r`n"

    AtomicWrite(LastInvalidPanelPath, Header Panel "`r`n----- PANEL_END -----`r`n")
}

FindLastOccurrence(Haystack, Needle)
{
    Position := 1
    Last := 0

    while Position := InStr(Haystack, Needle, true, Position)
    {
        Last := Position
        Position += StrLen(Needle)
    }

    return Last
}

Normalize(Text)
{
    Result := StrReplace(Text, "`r`n", "`n")
    return StrReplace(Result, "`r", "`n")
}

CountOccurrences(Haystack, Needle)
{
    Count := 0
    Position := 1

    while Position := InStr(Haystack, Needle, true, Position)
    {
        Count += 1
        Position += StrLen(Needle)
    }

    return Count
}

HasExactLine(Text, Expected)
{
    for Line in StrSplit(Normalize(Text), "`n")
    {
        if (Trim(Line, " `t`r") = Expected)
            return true
    }

    return false
}

GetHeaderValue(Text, Key)
{
    Prefix := Key "="

    for Line in StrSplit(Normalize(Text), "`n")
    {
        Clean := Trim(Line, " `t`r")

        if (SubStr(Clean, 1, StrLen(Prefix)) = Prefix)
            return Trim(SubStr(Clean, StrLen(Prefix) + 1))
    }

    return ""
}

HideToolTip()
{
    ToolTip
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
