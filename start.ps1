# Clypify Prospector — Start
# Registers a daily 07:00 scheduled task AND runs once immediately in the background.

$hermes = "C:\Users\WS\Desktop\projects\clypta\hermes"
$py     = (Get-Command py).Source
$stdout = "$hermes\output\prospector.log"
$stderr = "$hermes\output\prospector.err.log"

# --- Scheduled task (daily 07:00) ---
$existing = Get-ScheduledTask -TaskName "ClypifyProspector" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Scheduled task already registered. Skipping registration."
} else {
    $action   = New-ScheduledTaskAction -Execute $py -Argument "run.py" -WorkingDirectory $hermes
    $trigger  = New-ScheduledTaskTrigger -Daily -At "07:00"
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) -StartWhenAvailable
    Register-ScheduledTask -TaskName "ClypifyProspector" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "Scheduled task registered — runs daily at 07:00."
}

# --- Run once now in background ---
Write-Host "Running prospector now in background..."
Start-Process -FilePath $py -ArgumentList "run.py" -WorkingDirectory $hermes -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden
Write-Host "Done. Logs:"
Write-Host "  Stdout -> $stdout"
Write-Host "  Stderr -> $stderr"
Write-Host "To watch live: Get-Content '$stdout' -Wait"
