# Clypify Prospector — Stop
# Kills any running prospector process and unregisters the scheduled task.

# Kill background process if running
$procs = Get-Process -Name "py" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*run.py*" }

if ($procs) {
    $procs | Stop-Process -Force
    Write-Host "Stopped $($procs.Count) running prospector process(es)."
} else {
    Write-Host "No prospector process currently running."
}

# Unregister scheduled task
$existing = Get-ScheduledTask -TaskName "ClypifyProspector" -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName "ClypifyProspector" -Confirm:$false
    Write-Host "Scheduled task removed — daily runs cancelled."
} else {
    Write-Host "No scheduled task found."
}
