param(
  [int]$Port = 8000,
  [switch]$RunQA,
  [int]$AltPort = 0
)

$ErrorActionPreference = 'SilentlyContinue'

function Show-OwnerInfo([int]$p) {
  $procs = @()
  $cur = Get-CimInstance Win32_Process -Filter "ProcessId=$p"
  while ($cur) {
    $procs += $cur
    if (-not $cur.ParentProcessId -or $cur.ParentProcessId -eq 0) { break }
    $cur = Get-CimInstance Win32_Process -Filter "ProcessId=$($cur.ParentProcessId)"
  }

  "=== Process tree (child -> parent) ===" | Write-Host
  $procs | ForEach-Object {
    try { $cmd = ($_.CommandLine -replace '\s+', ' ') } catch { $cmd = '' }
    "{0,-7} {1,-25} {2}" -f $_.ProcessId, $_.Name, $cmd
  } | Write-Host

  $svc = Get-CimInstance Win32_Service -Filter "ProcessId=$p"
  if ($svc) {
    "`n=== Owning Windows Service ===" | Write-Host
    "{0} (Name={1}, StartMode={2}, State={3})" -f $svc.DisplayName, $svc.Name, $svc.StartMode, $svc.State | Write-Host
  }
  else {
    "`n(No Windows Service reported for PID $p)" | Write-Host
  }

  "`n=== Owners (exe paths) ===" | Write-Host
  $procs | ForEach-Object {
    try { $gp = Get-Process -Id $_.ProcessId -ErrorAction Stop; "{0,-7} {1,-20} {2}" -f $gp.Id, $gp.ProcessName, ($gp | Select-Object -ExpandProperty Path) } catch {}
  } | Write-Host
}

function Stop-PortListeners([int]$port) {
  $pids = (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
  if ($pids) { Stop-Process -Id $pids -Force -ErrorAction SilentlyContinue }
}

# 1) Inspect current owner
$conn = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -ErrorAction SilentlyContinue
if (-not $conn) {
  Write-Host "NO LISTENER on :$Port"
}
else {
  $ownerPid = $conn.OwningProcess
  Write-Host "Port :$Port listener PID: $ownerPid"
  Show-OwnerInfo -p $ownerPid

  # If a Windows Service owns the PID, try to stop and disable it first (clean stop)
  $owningSvc = Get-CimInstance Win32_Service -Filter "ProcessId=$ownerPid"
  if ($owningSvc) {
    Write-Host "Attempting to stop service: $($owningSvc.Name) ($($owningSvc.DisplayName))"
    try { Stop-Service -Name $owningSvc.Name -Force -ErrorAction Stop } catch { Write-Host "Stop-Service failed: $($_.Exception.Message)" }
    try { Set-Service -Name $owningSvc.Name -StartupType Disabled -ErrorAction Stop } catch { Write-Host "Set-Service failed: $($_.Exception.Message)" }
  }
}

# 2) Try to free the port robustly (up to 5 seconds)
$deadline = (Get-Date).AddSeconds(5)
while ( (Test-NetConnection 127.0.0.1 -Port $Port -WarningAction SilentlyContinue).TcpTestSucceeded -and (Get-Date) -lt $deadline ) {
  Stop-PortListeners -port $Port
  Start-Sleep -Milliseconds 250
}

if ( (Test-NetConnection 127.0.0.1 -Port $Port -WarningAction SilentlyContinue).TcpTestSucceeded ) {
  Write-Error "Port $Port is still BUSY - a respawner may still be active. Consider stopping the owning Windows Service or the top-most parent from the tree above."
  return
}
else {
  Write-Host "Port $Port is FREE."
}

# 3) Optionally run the full QA
if ($RunQA) {
  if ($AltPort -gt 0 -and $AltPort -ne $Port) {
    $env:API = "http://127.0.0.1:$AltPort"
    Write-Host "Using alternate API: $($env:API)"
  }
  powershell -ExecutionPolicy Bypass -NoLogo -NoProfile -File .\qa_run.ps1
  if (Test-Path .\qa_artifacts\summary.txt) {
    Get-Content -Raw .\qa_artifacts\summary.txt | Write-Host
  }
}

Write-Host "Done."
