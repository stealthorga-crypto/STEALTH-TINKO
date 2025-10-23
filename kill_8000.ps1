$p = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8000 -ErrorAction SilentlyContinue
if ($p) {
  $pids = $p | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
  foreach ($procId in $pids) {
    try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {}
  }
  'KILLED: ' + ($pids -join ',')
}
else {
  'NO-LISTENER'
}
