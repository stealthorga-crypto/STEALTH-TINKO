# One-shot repair for API port conflict and QA re-run
$ErrorActionPreference = 'SilentlyContinue'

function Kill-Port($port) {
  try {
    netstat -ano | Select-String (":" + $port + "\s") | ForEach-Object {
      if ($_.Line -match "\s+(\d+)$") { Stop-Process -Id $Matches[1] -Force -ErrorAction SilentlyContinue }
    }
  }
  catch {}
}

# 0) Kill anything on :8000, then wait until free (up to 5s)
$deadline = (Get-Date).AddSeconds(5)
Do {
  Kill-Port 8000
  Start-Sleep -Milliseconds 300
  $busy = netstat -ano | Select-String ':8000\s'
  if (-not $busy) { break }
} While ((Get-Date) -lt $deadline)

if ( netstat -ano | Select-String ':8000\s' ) {
  Write-Host 'Port 8000 still busy; re-run this block after closing any external server on :8000'
  exit 1
}

# 1) Quick router sanity: does maintenance route exist in last OpenAPI dump?
$openapiPath = Join-Path $PWD 'qa_artifacts\openapi.json'
if (Test-Path $openapiPath) {
  $raw = Get-Content $openapiPath -Raw
  if (-not ($raw -match '\/v1\/maintenance\/')) {
    Write-Host '[Hint] Maintenance route missing from OpenAPI. Ensure maintenance router is mounted.'
  }
}

# 2) Re-run full QA (non-hanging)
powershell -ExecutionPolicy Bypass -NoLogo -NoProfile -File .\qa_run.ps1

# 3) Show summary inline
Get-Content -Raw .\qa_artifacts\summary.txt
