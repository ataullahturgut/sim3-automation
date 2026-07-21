#Requires AutoHotkey v2.0
#SingleInstance Force

SetTitleMatchMode 2

global Root := A_Args.Length >= 1 ? RTrim(A_Args[1], "\/") : A_ScriptDir "\.."

global ReportsDir := Root "\REPORTS"
global CaptureResultPath := Root "\CAPTURE\LAST_CAPTURE_RESULT.txt"
global DeliveryResultPath := Root "\DELIVERY\LAST_DELIVERY_RESULT.txt"
global ResponseResultPath := Root "\RESPONSE\LAST_RESPONSE_WAIT_RESULT.txt"
global LoopResultPath := Root "\LOOP\LAST_LOOP_RESULT.txt"

global ColorBg := "F7F9FC"
global ColorText := "172033"
global ColorMuted := "6B778C"
global ColorBlue := "1268D6"
global ColorGreen := "10A65A"
global ColorRed := "E53935"
global ColorAmber := "D88700"
global ColorBorder := "DCE3EC"

global GuiObj := Gui("+AlwaysOnTop +ToolWindow -MaximizeBox -MinimizeBox", "GPT-Codex Otomasyonu")
GuiObj.MarginX := 12
GuiObj.MarginY := 10
GuiObj.BackColor := ColorBg
GuiObj.SetFont("s9 c" ColorText, "Segoe UI")

global TTitle := GuiObj.AddText("xm ym w286 h24 BackgroundTrans", "GPT-Codex Otomasyonu")
TTitle.SetFont("s12 bold c" ColorText, "Segoe UI")
global TCollapse := GuiObj.AddText("x+8 yp w28 h24 Center BackgroundTrans", "≪")
TCollapse.SetFont("s14 bold c" ColorMuted, "Segoe UI")

GuiObj.AddGroupBox("xm y+8 w330 h66 c" ColorBorder, "")
global TStatusTitle := GuiObj.AddText("xp+14 yp+14 w298 h22 BackgroundTrans", "HAZIR")
TStatusTitle.SetFont("s12 bold c" ColorBlue, "Segoe UI")
global TStatusDetail := GuiObj.AddText("xp y+2 w298 h18 BackgroundTrans", "Yeni görev bekleniyor")
TStatusDetail.SetFont("s9 c" ColorMuted, "Segoe UI")

GuiObj.AddGroupBox("xm y+8 w330 h78 c" ColorBorder, "")
global TTaskLabel := GuiObj.AddText("xp+14 yp+10 w290 h18 BackgroundTrans", "AKTİF GÖREV")
TTaskLabel.SetFont("s8 bold c" ColorMuted, "Segoe UI")
global TTaskShort := GuiObj.AddText("xp y+2 w290 h22 BackgroundTrans", "-")
TTaskShort.SetFont("s13 bold c" ColorText, "Segoe UI")
global TTaskName := GuiObj.AddText("xp y+1 w290 h20 BackgroundTrans", "Görev bekleniyor")
TTaskName.SetFont("s9 c" ColorMuted, "Segoe UI")

global TProgressTitle := GuiObj.AddText("xm y+10 w330 h20 BackgroundTrans", "İlerleme")
TProgressTitle.SetFont("s10 bold c" ColorText, "Segoe UI")

GuiObj.AddGroupBox("xm y+2 w330 h250 c" ColorBorder, "")

global StepLabels := [
    "Görev Alındı",
    "İnceleme Tamamlandı",
    "Değişiklikler Uygulandı",
    "Doğrulama Tamamlandı",
    "Rapor Hazırlandı",
    "Rapor ChatGPT'ye Gönderildi",
    "Rapor İnceleniyor",
    "Sonraki Görev Hazırlanıyor",
    "Yeni Komut Bekleniyor",
    "Yeni Görev Başlatılıyor"
]

global StepControls := []
global StepY := 238

Loop StepLabels.Length
{
    C := GuiObj.AddText("x42 y" StepY " w294 h20 BackgroundTrans", "○  " StepLabels[A_Index])
    C.SetFont("s9 c" ColorMuted, "Segoe UI")
    StepControls.Push(C)
    StepY += 23
}

global TInfoTitle := GuiObj.AddText("x12 y486 w330 h20 BackgroundTrans", "Bilgiler")
TInfoTitle.SetFont("s10 bold c" ColorText, "Segoe UI")

GuiObj.AddGroupBox("x12 y508 w102 h56 c" ColorBorder, "")
global TLoop := GuiObj.AddText("x18 y518 w90 h38 Center BackgroundTrans", "Döngü`n-")
TLoop.SetFont("s8 c" ColorBlue, "Segoe UI")

GuiObj.AddGroupBox("x122 y508 w102 h56 c" ColorBorder, "")
global TElapsed := GuiObj.AddText("x128 y518 w90 h38 Center BackgroundTrans", "Geçen Süre`n-")
TElapsed.SetFont("s8 c7A38D8", "Segoe UI")

GuiObj.AddGroupBox("x232 y508 w110 h56 c" ColorBorder, "")
global TUpdated := GuiObj.AddText("x238 y518 w98 h38 Center BackgroundTrans", "Son Güncelleme`n-")
TUpdated.SetFont("s8 c" ColorGreen, "Segoe UI")

global TExplanationTitle := GuiObj.AddText("xm y+10 w330 h20 BackgroundTrans", "Durum Açıklaması")
TExplanationTitle.SetFont("s10 bold c" ColorText, "Segoe UI")

GuiObj.AddGroupBox("xm y+2 w330 h64 c" ColorBorder, "")
global TExplanation := GuiObj.AddText("xp+12 yp+14 w304 h38 BackgroundTrans", "Yeni görev bekleniyor.")
TExplanation.SetFont("s8 c" ColorMuted, "Segoe UI")

global TRecentTitle := GuiObj.AddText("xm y+10 w330 h20 BackgroundTrans", "Son İşlemler")
TRecentTitle.SetFont("s10 bold c" ColorText, "Segoe UI")

GuiObj.AddGroupBox("xm y+2 w330 h82 c" ColorBorder, "")
global TRecent1 := GuiObj.AddText("xp+12 yp+12 w304 h18 BackgroundTrans", "• Yeni görev bekleniyor")
global TRecent2 := GuiObj.AddText("xp y+4 w304 h18 BackgroundTrans", "• Otomasyon hazır")
global TRecent3 := GuiObj.AddText("xp y+4 w304 h18 BackgroundTrans", "• Rapor durumu bekleniyor")

for C in [TRecent1, TRecent2, TRecent3]
    C.SetFont("s8 c" ColorMuted, "Segoe UI")

global TFooterVersion := GuiObj.AddText("xm y+10 w90 h18 BackgroundTrans", "v4.7")
TFooterVersion.SetFont("s8 c" ColorMuted, "Segoe UI")

global TFooterState := GuiObj.AddText("x+140 yp w100 h18 Right BackgroundTrans", "● READY")
TFooterState.SetFont("s9 bold c" ColorBlue, "Segoe UI")

GuiObj.Show("x14 y14 w354 h792 NoActivate")

SetTimer UpdateDashboard, 750
UpdateDashboard()

UpdateDashboard()
{
    global ReportsDir, CaptureResultPath, DeliveryResultPath, ResponseResultPath, LoopResultPath
    global TStatusTitle, TStatusDetail, TTaskShort, TTaskName
    global TLoop, TElapsed, TUpdated, TExplanation, TFooterState
    global TRecent1, TRecent2, TRecent3
    global StepControls

    LoopStatus := ReadLastKeyValue(LoopResultPath, "FINAL_STATUS")
    LoopReason := ReadLastKeyValue(LoopResultPath, "RESULT_REASON")
    LoopCurrent := ReadLastKeyValue(LoopResultPath, "CURRENT_LOOP")
    LoopMax := ReadLastKeyValue(LoopResultPath, "MAX_LOOPS")
    LoopState := ReadLastKeyValue(LoopResultPath, "LAST_STATE")
    LoopElapsed := ReadLastKeyValue(LoopResultPath, "ELAPSED_SECONDS")
    LastReport := ReadLastKeyValue(LoopResultPath, "LAST_REPORT")

    CaptureStatus := ReadLastKeyValue(CaptureResultPath, "FINAL_STATUS")
    DeliveryStatus := ReadLastKeyValue(DeliveryResultPath, "FINAL_STATUS")
    ResponseStatus := ReadLastKeyValue(ResponseResultPath, "FINAL_STATUS")

    ReadyTask := ReadJsonString(ReportsDir "\LATEST_READY.json", "task_id")
    ReadyReport := ReadJsonString(ReportsDir "\LATEST_READY.json", "report_filename")
    ReadyFinal := ReadJsonString(ReportsDir "\LATEST_READY.json", "final_status")

    if (ReadyTask = "")
        ReadyTask := "-"

    Overall := "READY"
    StatusTitle := "HAZIR"
    StatusDetail := "Yeni görev bekleniyor"
    Explanation := "Otomasyon yeni bir komut bekliyor."
    StepIndex := ReadyTask = "-" ? 0 : 1

    if (ReadyReport != "" || LastReport != "")
        StepIndex := Max(StepIndex, 5)

    if (CaptureStatus = "OK")
    {
        Overall := "RUNNING"
        StatusTitle := "RAPOR GÖNDERİLİYOR"
        StatusDetail := "Rapor ChatGPT'ye aktarılıyor"
        Explanation := "Rapor hazırlandı. Gönderim işlemi devam ediyor."
        StepIndex := Max(StepIndex, 6)
    }

    if (DeliveryStatus = "OK")
    {
        Overall := "WAITING"
        StatusTitle := "RAPOR İNCELENİYOR"
        StatusDetail := "Rapor ChatGPT'ye gönderildi"
        Explanation := "Rapor başarıyla gönderildi. İnceleme sonucu bekleniyor."
        StepIndex := Max(StepIndex, 7)
    }

    if (ResponseStatus = "OK")
    {
        Overall := "RUNNING"
        StatusTitle := "SONRAKİ GÖREV HAZIRLANIYOR"
        StatusDetail := "ChatGPT yanıtı alındı"
        Explanation := "Rapor incelemesi tamamlandı. Sonraki görev hazırlanıyor."
        StepIndex := Max(StepIndex, 8)
    }

    if (LoopStatus = "RUNNING")
    {
        Overall := "RUNNING"
        StatusTitle := "GÖREV ÇALIŞIYOR"
        StatusDetail := HumanStage(LoopState)
        Explanation := "Worker mevcut görevi kontrollü kapsam içinde yürütüyor."
        StepIndex := Max(StepIndex, StageFromLoopState(LoopState))
    }
    else if (LoopStatus = "OK")
    {
        Overall := "WAITING"
        StatusTitle := "YENİ KOMUT BEKLENİYOR"
        StatusDetail := "Mevcut otomasyon döngüsü tamamlandı"
        Explanation := "Rapor ve yanıt döngüsü tamamlandı. Yeni görev komutu bekleniyor."
        StepIndex := 9
    }
    else if (LoopStatus = "PAUSED")
    {
        Overall := "PAUSED"
        StatusTitle := "BEKLETİLDİ"
        StatusDetail := FriendlyReason(LoopReason)
        Explanation := "Otomasyon güvenli biçimde bekletildi. Durum kontrolü gerekiyor."
        StepIndex := Max(StepIndex, EvidenceStep(CaptureStatus, DeliveryStatus, ResponseStatus, ReadyReport))
    }
    else if (LoopStatus = "FAILED")
    {
        Overall := "BLOCKED"
        StatusTitle := "MÜDAHALE GEREKİYOR"
        StatusDetail := FriendlyReason(LoopReason)
        Explanation := FailureExplanation(LoopReason)
        StepIndex := Max(StepIndex, EvidenceStep(CaptureStatus, DeliveryStatus, ResponseStatus, ReadyReport))
    }

    TTaskShort.Text := ShortTaskId(ReadyTask)
    TTaskName.Text := FriendlyTask(ReadyTask)
    TStatusTitle.Text := StatusTitle
    TStatusDetail.Text := StatusDetail
    TExplanation.Text := Explanation

    ApplyStatusColors(Overall)

    LoopText := LoopCurrent = "" ? "-" : LoopCurrent " / " (LoopMax = "" ? "?" : LoopMax)
    TLoop.Text := "Döngü`n" LoopText
    TElapsed.Text := "Geçen Süre`n" FormatElapsed(LoopElapsed)
    TUpdated.Text := "Son Güncelleme`n" A_Hour ":" A_Min ":" A_Sec

    UpdateSteps(StepIndex, Overall)

    Recent := BuildRecent(LoopStatus, LoopReason, CaptureStatus, DeliveryStatus, ResponseStatus, ReadyReport, ReadyFinal)
    TRecent1.Text := Recent[1]
    TRecent2.Text := Recent[2]
    TRecent3.Text := Recent[3]
}

ApplyStatusColors(Overall)
{
    global TStatusTitle, TStatusDetail, TFooterState
    global ColorBlue, ColorGreen, ColorRed, ColorAmber, ColorMuted

    if (Overall = "BLOCKED")
    {
        TStatusTitle.SetFont("s12 bold c" ColorRed, "Segoe UI")
        TStatusDetail.SetFont("s9 c" ColorRed, "Segoe UI")
        TFooterState.Text := "● BLOCKED"
        TFooterState.SetFont("s9 bold c" ColorRed, "Segoe UI")
    }
    else if (Overall = "PAUSED")
    {
        TStatusTitle.SetFont("s12 bold c" ColorAmber, "Segoe UI")
        TStatusDetail.SetFont("s9 c" ColorAmber, "Segoe UI")
        TFooterState.Text := "● PAUSED"
        TFooterState.SetFont("s9 bold c" ColorAmber, "Segoe UI")
    }
    else if (Overall = "RUNNING")
    {
        TStatusTitle.SetFont("s12 bold c" ColorBlue, "Segoe UI")
        TStatusDetail.SetFont("s9 c" ColorBlue, "Segoe UI")
        TFooterState.Text := "● RUNNING"
        TFooterState.SetFont("s9 bold c" ColorGreen, "Segoe UI")
    }
    else if (Overall = "WAITING")
    {
        TStatusTitle.SetFont("s12 bold c" ColorBlue, "Segoe UI")
        TStatusDetail.SetFont("s9 c" ColorMuted, "Segoe UI")
        TFooterState.Text := "● WAITING"
        TFooterState.SetFont("s9 bold c" ColorBlue, "Segoe UI")
    }
    else
    {
        TStatusTitle.SetFont("s12 bold c" ColorBlue, "Segoe UI")
        TStatusDetail.SetFont("s9 c" ColorMuted, "Segoe UI")
        TFooterState.Text := "● READY"
        TFooterState.SetFont("s9 bold c" ColorBlue, "Segoe UI")
    }
}

UpdateSteps(StepIndex, Overall)
{
    global StepControls, StepLabels
    global ColorGreen, ColorBlue, ColorRed, ColorAmber, ColorMuted

    Loop StepControls.Length
    {
        Index := A_Index
        C := StepControls[Index]

        if (Index < StepIndex)
        {
            C.Text := "✓  " StepLabels[Index]
            C.SetFont("s9 c" ColorGreen, "Segoe UI")
        }
        else if (Index = StepIndex && StepIndex > 0)
        {
            Symbol := (Overall = "BLOCKED") ? "!" : "▶"
            Color := (Overall = "BLOCKED") ? ColorRed : ((Overall = "PAUSED") ? ColorAmber : ColorBlue)
            C.Text := Symbol "  " StepLabels[Index]
            C.SetFont("s9 bold c" Color, "Segoe UI")
        }
        else
        {
            C.Text := "○  " StepLabels[Index]
            C.SetFont("s9 c" ColorMuted, "Segoe UI")
        }
    }
}

BuildRecent(LoopStatus, LoopReason, CaptureStatus, DeliveryStatus, ResponseStatus, ReadyReport, ReadyFinal)
{
    Items := []

    if (LoopStatus = "FAILED")
        Items.Push("• " FriendlyReason(LoopReason))
    else if (LoopStatus = "PAUSED")
        Items.Push("• Otomasyon güvenli biçimde bekletildi")
    else if (LoopStatus = "RUNNING")
        Items.Push("• Görev çalışıyor")
    else if (LoopStatus = "OK")
        Items.Push("• Otomasyon döngüsü tamamlandı")

    if (ResponseStatus = "OK")
        Items.Push("• ChatGPT yanıtı alındı")
    if (DeliveryStatus = "OK")
        Items.Push("• Rapor ChatGPT'ye gönderildi")
    if (CaptureStatus = "OK")
        Items.Push("• Rapor gönderim için yakalandı")
    if (ReadyReport != "")
        Items.Push("• Tam rapor hazırlandı")
    if (ReadyFinal != "")
        Items.Push("• Worker sonucu: " Shorten(ReadyFinal, 36))

    while (Items.Length < 3)
        Items.Push("")

    return [Items[1], Items[2], Items[3]]
}

EvidenceStep(CaptureStatus, DeliveryStatus, ResponseStatus, ReadyReport)
{
    Step := 1
    if (ReadyReport != "")
        Step := 5
    if (CaptureStatus = "OK")
        Step := 6
    if (DeliveryStatus = "OK")
        Step := 7
    if (ResponseStatus = "OK")
        Step := 8
    return Step
}

StageFromLoopState(Value)
{
    Upper := StrUpper(Value)

    if InStr(Upper, "WAIT") && (InStr(Upper, "CMD") || InStr(Upper, "COMMAND") || InStr(Upper, "TASK"))
        return 9
    if InStr(Upper, "RESPONSE")
        return 7
    if InStr(Upper, "DELIVER") || InStr(Upper, "SEND")
        return 6
    if InStr(Upper, "REPORT")
        return 5
    if InStr(Upper, "TEST") || InStr(Upper, "VALIDAT")
        return 4
    if InStr(Upper, "APPLY") || InStr(Upper, "WRITE") || InStr(Upper, "CODEX")
        return 3
    if InStr(Upper, "AUDIT") || InStr(Upper, "READ") || InStr(Upper, "INSPECT")
        return 2

    return 2
}

HumanStage(Value)
{
    if (Value = "")
        return "Görev yürütülüyor"

    Text := StrReplace(Value, "WAIT_", "")
    Text := StrReplace(Text, "_", " ")
    return Shorten(Text, 42)
}

FailureExplanation(Value)
{
    Upper := StrUpper(Value)

    if InStr(Upper, "CAPTURE") && InStr(Upper, "TIMEOUT")
        return "Beklenen içerik zamanında doğrulanamadı. Yakalama tamamlanamadı."
    if InStr(Upper, "SEND") || InStr(Upper, "DELIVERY")
        return "Rapor gönderimi tamamlanamadı. Gönderim durumu kontrol edilmeli."
    if InStr(Upper, "RESPONSE")
        return "ChatGPT yanıtı zamanında doğrulanamadı."
    if InStr(Upper, "CODEX")
        return "Codex çalışması tamamlanamadı. Hata raporu incelenmeli."

    return "Otomasyon kontrollü biçimde durdu. Son run kanıtı incelenmeli."
}

FriendlyReason(Value)
{
    if (Value = "")
        return "Durum ayrıntısı bulunamadı"

    Upper := StrUpper(Value)

    if InStr(Upper, "CAPTURE") && InStr(Upper, "TIMEOUT")
        return "Rapor yakalama zaman aşımı"
    if InStr(Upper, "SEND_NOT_READY")
        return "Gönderme alanı hazır olmadı"
    if InStr(Upper, "PAUSED")
        return "Otomasyon bekletildi"
    if InStr(Upper, "USER EMERGENCY STOP")
        return "Kullanıcı tarafından durduruldu"

    return Shorten(StrReplace(Value, "_", " "), 44)
}

ShortTaskId(Task)
{
    if (Task = "" || Task = "-")
        return "-"

    Phase := ""
    Code := ""

    if RegExMatch(Task, "i)(FH\d+)", &M1)
        Phase := StrUpper(M1[1])

    if RegExMatch(Task, "i)(\d{3}[A-Z]\d*)", &M2)
        Code := StrUpper(M2[1])

    if (Phase != "" && Code != "")
        return Phase " · " Code

    return Shorten(StrReplace(Task, "_", " "), 26)
}

FriendlyTask(Task)
{
    if (Task = "" || Task = "-")
        return "Görev bekleniyor"

    if InStr(Task, "AKINSOFT_IMPORT_WORKFLOW")
        return "Akinsoft Import Workflow"
    if InStr(Task, "PERIOD_PROFITABILITY_WORKFLOW")
        return "Period Profitability Workflow"
    if InStr(Task, "HANDLER_CLEANUP")
        return "Logging Handler Cleanup"
    if InStr(Task, "FAILURE_TAXONOMY")
        return "Failure Taxonomy"
    if InStr(Task, "OPERATION_CONTEXT")
        return "Operation Context Lifecycle"

    Text := StrReplace(Task, "SIM3_", "")
    Text := StrReplace(Text, "_BATCH", "")
    Text := StrReplace(Text, "_", " ")
    return Shorten(Text, 38)
}

ReadLastKeyValue(Path, Key)
{
    if !FileExist(Path)
        return ""

    try
        Text := FileRead(Path, "UTF-8")
    catch
        return ""

    if RegExMatch(Text, "(?m)^" Key "=(.*)$", &M)
        return Trim(M[1])

    return ""
}

ReadJsonString(Path, Key)
{
    if !FileExist(Path)
        return ""

    try
        Text := FileRead(Path, "UTF-8")
    catch
        return ""

    if RegExMatch(Text, '"' Key '"\s*:\s*"([^"]*)"', &M)
        return M[1]

    return ""
}

FormatElapsed(Value)
{
    if (Value = "")
        return "-"

    Seconds := Integer(Value)
    Hours := Floor(Seconds / 3600)
    Minutes := Floor(Mod(Seconds, 3600) / 60)
    Sec := Mod(Seconds, 60)

    if (Hours > 0)
        return Hours " sa " Minutes " dk"
    if (Minutes > 0)
        return Minutes " dk " Sec " sn"

    return Sec " sn"
}

Shorten(Value, MaxLen)
{
    if (Value = "")
        return ""

    if (StrLen(Value) <= MaxLen)
        return Value

    return SubStr(Value, 1, MaxLen - 3) "..."
}