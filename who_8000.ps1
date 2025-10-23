param(
  [int]$Port = 8000
)

# Diagnose who owns 127.0.0.1:$Port, show parent chain, and detect Windows Service ownership
try {
  $conn = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -ErrorAction SilentlyContinue
}
catch {
  $conn = $null
}

if (-not $conn) {
  Write-Host "NO LISTENER on :$Port"
  return
}

$ownerPid = $conn.OwningProcess
Write-Host "Port :$Port listener PID: $ownerPid"

# Build process tree (child -> parent)
$procs = @()
$cur = Get-CimInstance Win32_Process -Filter "ProcessId=$ownerPid"
while ($cur) {
  $procs += $cur
  if (-not $cur.ParentProcessId -or $cur.ParentProcessId -eq 0) { break }
  $cur = Get-CimInstance Win32_Process -Filter "ProcessId=$($cur.ParentProcessId)"
}

"=== Process tree (child → parent) ===" | Write-Host
$procs | ForEach-Object {
  try {
    $cmd = ($_.CommandLine -replace '\s+', ' ')
  }
  catch { $cmd = '' }
  "{0,-7} {1,-25} {2}" -f $_.ProcessId, $_.Name, $cmd
} | Write-Host

# Is it a Windows Service?
$svc = Get-CimInstance Win32_Service -Filter "ProcessId=$ownerPid"
if ($svc) {
  "`n=== Owning Windows Service ===" | Write-Host
  "{0} (Name={1}, StartMode={2}, State={3})" -f $svc.DisplayName, $svc.Name, $svc.StartMode, $svc.State | Write-Host
}
else {
  "`n(No Windows Service reported for PID $ownerPid)" | Write-Host
}

"`n=== Owners (exe paths) ===" | Write-Host
$procs | ForEach-Object {
  try {
    $p = Get-Process -Id $_.ProcessId -ErrorAction Stop
    "{0,-7} {1,-20} {2}" -f $p.Id, $p.ProcessName, ($p | Select-Object -ExpandProperty Path)
  }
  catch {}
} | Write-Host

Write-Host "`nHints:"
Write-Host "- If a Windows Service is shown above, that's likely the respawner (Stop-Service -Name <Name> -Force; Set-Service -Name <Name> -StartupType Disabled)."
Write-Host "- Otherwise, the top-most parent in the tree is likely the respawner (Stop-Process -Id <TopParentPid> -Force)."

