#Requires AutoHotkey v2.0
#SingleInstance Force
#ErrorStdOut
OnError(SIM3_FullFixUnhandledErrorV3)
CoordMode "Mouse", "Screen"
CoordMode "Pixel", "Screen"
SetTitleMatchMode 2

global Root := A_Args.Length >= 1 ? RTrim(A_Args[1], "\/") : A_ScriptDir "\.."
global ResponseDir := Root "\RESPONSE"
global DeliveryResultPath := Root "\DELIVERY\LAST_DELIVERY_RESULT.txt"
global ResponseResultPath := ResponseDir "\LAST_RESPONSE_WAIT_RESULT.txt"
global ResponseTokenPath := ResponseDir "\CURRENT_RESPONSE_TOKEN.txt"
global ResponseRunToken := FileExist(ResponseTokenPath) ? Trim(FileRead(ResponseTokenPath, "UTF-8")) : ""
global ResponseOwnerPid := DllCall("GetCurrentProcessId", "UInt")
global ResponseWaitTimeoutMs := 720000
global ResponseWaitElapsedMs := 0
global TemplateDir := Root "\RESPONSE\TEMPLATES"
global StopIconTemplate := TemplateDir "\SIM3_CHATGPT_STOP_ICON_TEMPLATE.png"
global CopyIconTemplate := TemplateDir "\SIM3_CHATGPT_COPY_ICON_TEMPLATE.png"
global ActionPairTemplate := TemplateDir "\SIM3_CHATGPT_WRITING_PANEL_ACTION_PAIR_TEMPLATE.png"

global StartedAt := A_Now
global StartTick := DllCall("GetTickCount64", "UInt64")
global LastState := "INITIALIZING"
global BrowserHwndUsed := 0
global BrowserTitleUsed := ""
global DeliveryStatusSeen := ""
global DeliveryReasonSeen := ""
global StopSearchCount := 0
global StopFoundCount := 0
global CopySearchCount := 0
global CopyFoundCount := 0
global ActionPairSearchCount := 0
global ActionPairFoundCount := 0
global StableCompleteCount := 0
global CompletionEvidence := "NONE"
global GenerationObserved := false
global MinimumCompletionDelayMs := 12000

Hotkey "^!x", EmergencyStop

if !DirExist(ResponseDir)
    DirCreate ResponseDir

WriteStatus("STARTING", "INITIALIZING")

if (ResponseRunToken = "")
    Finish("FAILED", "RESPONSE_RUN_TOKEN_NOT_FOUND", 70)

if !FileExist(StopIconTemplate)
    Finish("FAILED", "STOP_ICON_TEMPLATE_NOT_FOUND", 71)

if !FileExist(CopyIconTemplate)
    Finish("FAILED", "COPY_ICON_TEMPLATE_NOT_FOUND", 72)

if !FileExist(ActionPairTemplate)
    Finish("FAILED", "ACTION_PAIR_TEMPLATE_NOT_FOUND", 73)

if !WaitForDeliveryOk()
    Finish("PAUSED", "DELIVERY_OK_NOT_SEEN_BEFORE_TIMEOUT", 30)

BrowserHwnd := FindBrowserWindow()

if !BrowserHwnd
    Finish("FAILED", "CHATGPT_BROWSER_WINDOW_NOT_FOUND", 74)

BrowserHwndUsed := BrowserHwnd
BrowserTitleUsed := WinGetTitle("ahk_id " BrowserHwnd)

WinActivate "ahk_id " BrowserHwnd

if !WinWaitActive("ahk_id " BrowserHwnd, , 5)
    Finish("FAILED", "BROWSER_ACTIVATION_FAILED", 75)

ScrollToBottom(BrowserHwnd)
Sleep 1000

WriteStatus("WAITING", "WAITING_RESPONSE_COMPLETE_BY_ICON_STATE")

if WaitForResponseCompleteByIcons(BrowserHwnd)
    Finish("OK", "RESPONSE_COMPLETE_ICON_STATE_STABLE", 0)

Finish("PAUSED", "RESPONSE_COMPLETE_NOT_CONFIRMED_BEFORE_TIMEOUT", 31)

WaitForDeliveryOk()
{
    global DeliveryResultPath, DeliveryStatusSeen, DeliveryReasonSeen, LastState

    Deadline := A_TickCount + 240000

    Loop
    {
        DeliveryStatusSeen := ReadLastKeyValue(DeliveryResultPath, "FINAL_STATUS")
        DeliveryReasonSeen := ReadLastKeyValue(DeliveryResultPath, "RESULT_REASON")
        LastState := "WAIT_DELIVERY_" DeliveryStatusSeen
        WriteStatus("WAITING", "WAITING_DELIVERY_OK")

        if (DeliveryStatusSeen = "OK")
            return true

        if (DeliveryStatusSeen = "FAILED") || (DeliveryStatusSeen = "PAUSED")
            return false

        if (A_TickCount > Deadline)
            return false

        Sleep 1500
    }
}

WaitForResponseCompleteByIcons(BrowserHwnd)
{
    global StableCompleteCount, CompletionEvidence, LastState
    global ResponseWaitTimeoutMs, ResponseWaitElapsedMs, GenerationObserved, MinimumCompletionDelayMs

    WaitStartedTick64 := DllCall("GetTickCount64", "UInt64")

    Loop
    {
        ResponseWaitElapsedMs := DllCall("GetTickCount64", "UInt64") - WaitStartedTick64
        LastState := "IMAGE_STATE_SCAN"
        ScrollToBottom(BrowserHwnd)

        StopVisible := FindStopIcon(BrowserHwnd)
        CopyVisible := FindCopyIcon(BrowserHwnd)
        ActionPairVisible := FindActionPair(BrowserHwnd)

        if StopVisible
        {
            GenerationObserved := true
            StableCompleteCount := 0
            CompletionEvidence := "STOP_ICON_VISIBLE_GENERATING"
            WriteStatus("WAITING", "STOP_ICON_VISIBLE_GENERATING")
        }
        else if CopyVisible
        {
            if GenerationObserved || (ResponseWaitElapsedMs >= MinimumCompletionDelayMs)
            {
                StableCompleteCount += 1
                CompletionEvidence := "COPY_ICON_VISIBLE_STOP_ABSENT"
                WriteStatus("WAITING", "COPY_ICON_VISIBLE_STOP_ABSENT")
            }
            else
            {
                StableCompleteCount := 0
                CompletionEvidence := "PREEXISTING_COPY_BEFORE_RESPONSE_START"
                WriteStatus("WAITING", "WAITING_RESPONSE_START_EVIDENCE")
            }
        }
        else if ActionPairVisible
        {
            if GenerationObserved || (ResponseWaitElapsedMs >= MinimumCompletionDelayMs)
            {
                StableCompleteCount += 1
                CompletionEvidence := "ACTION_PAIR_VISIBLE_STOP_ABSENT"
                WriteStatus("WAITING", "ACTION_PAIR_VISIBLE_STOP_ABSENT")
            }
            else
            {
                StableCompleteCount := 0
                CompletionEvidence := "PREEXISTING_ACTION_PAIR_BEFORE_RESPONSE_START"
                WriteStatus("WAITING", "WAITING_RESPONSE_START_EVIDENCE")
            }
        }
        else
        {
            StableCompleteCount := 0
            CompletionEvidence := "NO_COMPLETION_ICON_FOUND"
            WriteStatus("WAITING", "NO_COMPLETION_ICON_FOUND")
        }

        ; Write the terminal OK state before returning so the controller cannot
        ; observe a completed counter followed by an ambiguous/intermediate file.
        if (StableCompleteCount >= 2)
        {
            LastState := "RESPONSE_COMPLETE_ICON_STATE_STABLE"
            WriteStatus("OK", "RESPONSE_COMPLETE_ICON_STATE_STABLE")
            return true
        }

        ; GetTickCount64 avoids absolute-deadline/wrap ambiguity.
        if (ResponseWaitElapsedMs >= ResponseWaitTimeoutMs)
        {
            LastState := "RESPONSE_WAIT_TIMEOUT"
            WriteStatus("PAUSED", "RESPONSE_COMPLETE_NOT_CONFIRMED_BEFORE_TIMEOUT")
            return false
        }

        Sleep 1800
    }
}

FindStopIcon(BrowserHwnd)
{
    global StopIconTemplate, StopSearchCount, StopFoundCount

    Rect := GetInputAreaSearchRect(BrowserHwnd)
    if !Rect
        return false

    FoundX := 0
    FoundY := 0
    StopSearchCount += 1

    try
        Found := ImageSearch(&FoundX, &FoundY, Rect.Left, Rect.Top, Rect.Right, Rect.Bottom, "*90 *TransWhite " StopIconTemplate)
    catch
        return false

    if Found
    {
        StopFoundCount += 1
        return true
    }

    return false
}

FindCopyIcon(BrowserHwnd)
{
    global CopyIconTemplate, CopySearchCount, CopyFoundCount

    Rect := GetAssistantActionSearchRect(BrowserHwnd)
    if !Rect
        return false

    FoundX := 0
    FoundY := 0
    CopySearchCount += 1

    try
        Found := ImageSearch(&FoundX, &FoundY, Rect.Left, Rect.Top, Rect.Right, Rect.Bottom, "*90 *TransWhite " CopyIconTemplate)
    catch
        return false

    if Found
    {
        CopyFoundCount += 1
        return true
    }

    return false
}

FindActionPair(BrowserHwnd)
{
    global ActionPairTemplate, ActionPairSearchCount, ActionPairFoundCount

    Rect := GetAssistantActionSearchRect(BrowserHwnd)
    if !Rect
        return false

    FoundX := 0
    FoundY := 0
    ActionPairSearchCount += 1

    try
        Found := ImageSearch(&FoundX, &FoundY, Rect.Left, Rect.Top, Rect.Right, Rect.Bottom, "*90 *TransWhite " ActionPairTemplate)
    catch
        return false

    if Found
    {
        ActionPairFoundCount += 1
        return true
    }

    return false
}

GetInputAreaSearchRect(BrowserHwnd)
{
    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return false

    Rect := {}
    Rect.Left := ClientX + Floor(ClientW * 0.30)
    Rect.Right := ClientX + Floor(ClientW * 0.78)
    Rect.Top := ClientY + Floor(ClientH * 0.78)
    Rect.Bottom := ClientY + ClientH - 10
    return Rect
}

GetAssistantActionSearchRect(BrowserHwnd)
{
    try
        WinGetClientPos &ClientX, &ClientY, &ClientW, &ClientH, "ahk_id " BrowserHwnd
    catch
        return false

    Rect := {}
    Rect.Left := ClientX + Floor(ClientW * 0.25)
    Rect.Right := ClientX + Floor(ClientW * 0.82)
    ; V4.7R1: after Ctrl+End, prefer lower/newer assistant action icons.
    Rect.Top := ClientY + Floor(ClientH * 0.28)
    Rect.Bottom := ClientY + Floor(ClientH * 0.90)
    return Rect
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

    ; V4.7R1: force the newest response area in long conversations.
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

ReadLastKeyValue(Path, Key)
{
    if !FileExist(Path)
        return ""

    Text := FileRead(Path, "UTF-8")
    Pattern := "(?m)^" Key "=(.*)$"

    if RegExMatch(Text, Pattern, &M)
        return Trim(M[1])

    return ""
}

WriteStatus(Status, Reason)
{
    global ResponseResultPath, StartedAt, StartTick, LastState, BrowserHwndUsed, BrowserTitleUsed
    global DeliveryStatusSeen, DeliveryReasonSeen
    global StopSearchCount, StopFoundCount, CopySearchCount, CopyFoundCount
    global ActionPairSearchCount, ActionPairFoundCount, StableCompleteCount, CompletionEvidence
    global ResponseRunToken, ResponseOwnerPid, ResponseWaitTimeoutMs, ResponseWaitElapsedMs
    global GenerationObserved, MinimumCompletionDelayMs

    Elapsed := Floor((DllCall("GetTickCount64", "UInt64") - StartTick) / 1000)

    Text := ""
    Text .= "STEP=SIM3_V4_2_RESPONSE_WAIT`r`n"
    Text .= "METHOD=IMAGE_SEARCH_NO_CTRL_A_V4_7_UNIFIED_TOKEN_OWNED`r`n"
    Text .= "RUN_TOKEN=" ResponseRunToken "`r`n"
    Text .= "OWNER_PID=" ResponseOwnerPid "`r`n"
    Text .= "STARTED_AT=" StartedAt "`r`n"
    Text .= "UPDATED_AT=" A_Now "`r`n"
    Text .= "ELAPSED_SECONDS=" Elapsed "`r`n"
    Text .= "BROWSER_TITLE_USED=" BrowserTitleUsed "`r`n"
    Text .= "BROWSER_HWND_USED=" BrowserHwndUsed "`r`n"
    Text .= "DELIVERY_STATUS_SEEN=" DeliveryStatusSeen "`r`n"
    Text .= "DELIVERY_REASON_SEEN=" DeliveryReasonSeen "`r`n"
    Text .= "STOP_ICON_SEARCH_COUNT=" StopSearchCount "`r`n"
    Text .= "STOP_ICON_FOUND_COUNT=" StopFoundCount "`r`n"
    Text .= "COPY_ICON_SEARCH_COUNT=" CopySearchCount "`r`n"
    Text .= "COPY_ICON_FOUND_COUNT=" CopyFoundCount "`r`n"
    Text .= "ACTION_PAIR_SEARCH_COUNT=" ActionPairSearchCount "`r`n"
    Text .= "ACTION_PAIR_FOUND_COUNT=" ActionPairFoundCount "`r`n"
    Text .= "STABLE_COMPLETE_COUNT=" StableCompleteCount "`r`n"
    Text .= "COMPLETION_EVIDENCE=" CompletionEvidence "`r`n"
    Text .= "SCROLL_POLICY=CTRL_END_END_WHEELDOWN_8`r`n"
    Text .= "STABLE_COMPLETE_REQUIRED=2`r`n"
    Text .= "RESPONSE_WAIT_TIMEOUT_MS=" ResponseWaitTimeoutMs "`r`n"
    Text .= "RESPONSE_WAIT_ELAPSED_MS=" ResponseWaitElapsedMs "`r`n"
    Text .= "GENERATION_OBSERVED=" (GenerationObserved ? "True" : "False") "`r`n"
    Text .= "MINIMUM_COMPLETION_DELAY_MS=" MinimumCompletionDelayMs "`r`n"
    Text .= "LAST_STATE=" LastState "`r`n"
    Text .= "RESULT_REASON=" Reason "`r`n"
    Text .= "FINAL_STATUS=" Status "`r`n"

    AtomicWrite(ResponseResultPath, Text)
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
    Finish("PAUSED", "USER_EMERGENCY_STOP", 30)
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
