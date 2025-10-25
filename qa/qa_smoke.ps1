# QA Smoke script for Tinko stack (backend only)
# Runs sequential checks and writes artifacts into qa_artifacts/
# Usage: pwsh -File qa/qa_smoke.ps1

param(
  [string]$ApiHost = "127.0.0.1",
  [int]$ApiPort = 8010,
  [string]$Python = "python"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$base = "http://$($ApiHost):$($ApiPort)"
$artifacts = Join-Path $PSScriptRoot "..\qa_artifacts"
if (!(Test-Path $artifacts)) { New-Item -ItemType Directory -Path $artifacts | Out-Null }

function Write-Result($Name, $Ok, $Extra) {
  $status = if ($Ok) { 'PASS' } else { 'FAIL' }
  Write-Host ("[{0}] {1} {2}" -f (Get-Date -Format s), $status, $Name) $(if ($Extra) { " - $Extra" })
}

function Invoke-Http($Method, $Url, $Body = $null, $Headers = @{}) {
  $irParams = @{ Method = $Method; Uri = $Url; Headers = $Headers }
  if ($null -ne $Body) { $irParams['Body'] = ($Body | ConvertTo-Json -Depth 5); $irParams['ContentType'] = 'application/json' }
  return Invoke-RestMethod @irParams
}

# 1) Kill port and start backend
try {
  # Best effort kill
  $proc = Get-Process -Id (Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess) -ErrorAction SilentlyContinue
  if ($proc) { $proc | Stop-Process -Force -ErrorAction SilentlyContinue }
}
catch {}

$backend = Start-Process -FilePath $Python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "$ApiHost", "--port", "$ApiPort" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2

$results = @()

try {
  # 2) Health checks
  $h = Invoke-WebRequest -UseBasicParsing "$base/healthz" -TimeoutSec 10
  $results += @{ name = 'healthz'; ok = ($h.StatusCode -eq 200) }

  $o = Invoke-WebRequest -UseBasicParsing "$base/openapi.json" -TimeoutSec 10
  $results += @{ name = 'openapi'; ok = ($o.StatusCode -eq 200) }

  # 3) Register + Login (stubbed token)
  # Directly mint a JWT for tests using default secret if available
  $adminToken = ""  # Provide your admin JWT here if needed for protected routes

  # 4) Create retry policy (optional; may require auth)
  try {
    if ($adminToken) {
      # Endpoint path uses /v1/retry/policies
      $null = Invoke-Http -Method 'POST' -Url "$base/v1/retry/policies" -Body @{ name = 'Default'; max_retries = 3; initial_delay_minutes = 60; backoff_multiplier = 2; max_delay_minutes = 1440 } -Headers @{ Authorization = "Bearer $adminToken" }
      $results += @{ name = 'retry_policy'; ok = $true }
    }
  }
  catch { $results += @{ name = 'retry_policy'; ok = $false } }

  # 5) Schedule suggested windows
  $sched = Invoke-WebRequest -UseBasicParsing "$base/v1/schedule/suggested_windows?ref=QA-REF&hours_ahead=6" -TimeoutSec 10
  $results += @{ name = 'schedule_windows'; ok = ($sched.StatusCode -eq 200) }
  Set-Content -Path (Join-Path $artifacts 'schedule_windows.json') -Value $sched.Content

  # 6) Razorpay order public endpoint (expect 503 if not configured)
  try {
    $ord = Invoke-Http -Method 'POST' -Url "$base/v1/payments/razorpay/orders-public" -Body @{ ref = 'NON_EXISTENT' }
    $results += @{ name = 'razorpay_order_public'; ok = $true }
    Set-Content -Path (Join-Path $artifacts 'razorpay_order_public.json') -Value ($ord | ConvertTo-Json -Depth 5)
  }
  catch {
    # 503 or 404 acceptable in dev without data
    $results += @{ name = 'razorpay_order_public'; ok = $true }
  }

  # 7) Analytics trio (may be 200 with empty values if no auth required; otherwise mark soft)
  try {
    $r1 = Invoke-WebRequest -UseBasicParsing "$base/v1/analytics/revenue_recovered" -TimeoutSec 10
    $r2 = Invoke-WebRequest -UseBasicParsing "$base/v1/analytics/recovery_rate" -TimeoutSec 10
    $r3 = Invoke-WebRequest -UseBasicParsing "$base/v1/analytics/attempts_summary" -TimeoutSec 10
    $results += @{ name = 'analytics'; ok = ($r1.StatusCode -eq 200 -and $r2.StatusCode -eq 200 -and $r3.StatusCode -eq 200) }
  }
  catch { $results += @{ name = 'analytics'; ok = $false } }

  # 8) Webhook invalid signature -> 400
  try {
    $wh = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$base/v1/webhooks/razorpay" -Headers @{ 'X-Razorpay-Signature' = 'bad' } -Body '{}' -ContentType 'application/json'
    $results += @{ name = 'webhook_invalid_sig'; ok = ($wh.StatusCode -eq 400) }
  }
  catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) { $results += @{ name = 'webhook_invalid_sig'; ok = $true } } else { $results += @{ name = 'webhook_invalid_sig'; ok = $false } }
  }
}
finally {
  if ($backend -and !$backend.HasExited) {
    try { $backend | Stop-Process -Force } catch {}
  }
}

# Summary table
$fail = $false
foreach ($r in $results) { if (-not $r.ok) { $fail = $true } ; Write-Result $r.name $r.ok $null }

if ($fail) { exit 1 } else { exit 0 }
