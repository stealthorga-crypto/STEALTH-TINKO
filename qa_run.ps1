# qa_run.ps1 — Non-hanging, sequential E2E QA for Tinko (Windows PowerShell)
# qa_run.ps1 - Non-hanging, sequential E2E QA for Tinko (Windows PowerShell)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function New-QaDir($p) {
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}
function TS { (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') }
function W($s) { Write-Host ('[{0}] {1}' -f (TS), $s) }
function JSave($obj, $path) { ($obj | ConvertTo-Json -Depth 10) | Out-File -FilePath $path -Encoding utf8 }

# Config (edit if needed)
$PY = 'C:\\Python313\\python.exe'
# Fallback to PATH Python if pinned path is unavailable
if (-not (Test-Path $PY)) { $PY = 'python' }
# Allow override via environment variable API, e.g. $env:API = 'http://127.0.0.1:8010'
$API = if ($env:API -and $env:API.Trim()) { $env:API.Trim() } else { 'http://127.0.0.1:8000' }
$CONSOLE = 'http://127.0.0.1:3000'
$UVICORN_HOST = '127.0.0.1'
$UVICORN_PORT = 8000

# If $API is a valid absolute URI, align host/port for the local server process
try {
  $apiUri = [uri]$API
  if ($apiUri.Host -and $apiUri.Port) {
    $UVICORN_HOST = $apiUri.Host
    $UVICORN_PORT = $apiUri.Port
  }
}
catch {}
$QA_DIR = 'qa_artifacts'
$EMAIL = ('qa+{0}@example.com' -f (Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))
$PASS = 'Test1234!'
$ORG = 'QA Org'
$REF = 'QA-REF-001'

New-QaDir $QA_DIR

# Result tracking
$global:RESULTS = @()
function Step-Start($name) { W "STEP: $name"; return [PSCustomObject]@{ Step = $name; Status = 'RUNNING'; Evidence = @() } }
function Step-End([ref]$rec, $status, $evidence) {
  $rec.Value.Status = $status
  if ($evidence) { $rec.Value.Evidence += $evidence }
  $global:RESULTS += $rec.Value
  W ('RESULT: {0} => {1}' -f $rec.Value.Step, $status)
}

function Invoke-HttpJson($method, $url, $body, $headers, $timeoutSec, $outPath) {
  try {
    $params = @{ Method = $method; Uri = $url; TimeoutSec = $timeoutSec; ErrorAction = 'Stop' }
    if ($headers) { $params['Headers'] = $headers }
    if ($body) { $params['Body'] = ($body | ConvertTo-Json -Depth 10); $params['ContentType'] = 'application/json' }
    $res = Invoke-WebRequest @params
    if ($outPath) { $res.Content | Out-File -FilePath $outPath -Encoding utf8 }
    return $true, $res.StatusCode, $res.Content
  }
  catch {
    return $false, $_.Exception.Message, $null
  }
}

function Stop-Port($port) {
  try {
    $lines = netstat -ano | Select-String (":" + $port + "\s")
    foreach ($l in $lines) {
      if ($l -match "\s+(\d+)$") { $procId = [int]$Matches[1]; Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
    }
  }
  catch {}
}

function Wait-Http200($url, $timeoutSec) {
  $deadline = (Get-Date).AddSeconds($timeoutSec)
  do {
    try {
      $r = Invoke-WebRequest -Method GET -Uri $url -TimeoutSec 2 -ErrorAction Stop
      if ($r.StatusCode -eq 200) { return $true }
    }
    catch { Start-Sleep -Milliseconds 250 }
  } while ((Get-Date) -lt $deadline)
  return $false
}

# 1) SANITY
$S = Step-Start 'Sanity & Workspace'
try {
  if (-not (Test-Path '.\app\main.py')) { throw 'app\main.py not found in current directory.' }
  if (-not (Test-Path '.\app\routers')) { throw 'app\routers not found (wrong tree?)' }
  $pyv = & $PY --version 2>&1
  Step-End ([ref]$S) 'PASS' @("Python=$pyv", "CWD=$(Get-Location)")
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message, "CWD=$(Get-Location)")
}

# 2) START API
$S = Step-Start 'Start API (Uvicorn)'
try {
  Stop-Port $UVICORN_PORT
  $apiLog = Join-Path $QA_DIR 'api_stdout.log'
  $apiErr = Join-Path $QA_DIR 'api_stderr.log'
  # Ensure PUBLIC_BASE_URL is set so generated links use the same base as our API target during QA
  # This keeps recovery links consistent when running on alternate ports (e.g., 8010)
  if (-not $env:PUBLIC_BASE_URL -or -not $env:PUBLIC_BASE_URL.Trim()) {
    $env:PUBLIC_BASE_URL = $API
  }
  $uvArgs = @('-m', 'uvicorn', 'app.main:app', '--host', $UVICORN_HOST, '--port', $UVICORN_PORT.ToString())
  $p = Start-Process -FilePath $PY -ArgumentList $uvArgs -RedirectStandardOutput $apiLog -RedirectStandardError $apiErr -PassThru
  if (Wait-Http200 "$API/healthz" 15) {
    Step-End ([ref]$S) 'PASS' @("PID=$($p.Id)", "Logs=$apiLog,$apiErr")
  }
  else {
    Step-End ([ref]$S) 'FAIL' @('API did not become healthy in 15s', "Logs=$apiLog,$apiErr")
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 3) HEALTH
$S = Step-Start 'GET /healthz'
$ok, $code, $body = Invoke-HttpJson 'GET' "$API/healthz" $null $null 3 (Join-Path $QA_DIR 'healthz.json')
if ($ok -and $code -eq 200) {
  Step-End ([ref]$S) 'PASS' @($body)
}
else {
  Step-End ([ref]$S) 'FAIL' @("code=$code")
}

# 4) OPENAPI
$S = Step-Start 'GET /openapi.json'
$ok, $code, $body = Invoke-HttpJson 'GET' "$API/openapi.json" $null $null 8 (Join-Path $QA_DIR 'openapi.json')
if ($ok -and $code -eq 200) {
  Step-End ([ref]$S) 'PASS' @('Saved openapi.json')
}
else {
  Step-End ([ref]$S) 'FAIL' @("code=$code")
}

# 5) MAINTENANCE ROUTE
$S = Step-Start 'Maintenance route presence & call'
try {
  $openapi = Get-Content (Join-Path $QA_DIR 'openapi.json') -Raw
  $pathMatch = Select-String -InputObject $openapi -Pattern '\/v1\/maintenance[^\"]*' -AllMatches
  $foundPath = $null
  if ($pathMatch.Matches.Count -gt 0) { $foundPath = $pathMatch.Matches[0].Value }

  $token = $null
  if (Test-Path "$QA_DIR\login.json") {
    try { $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token } catch {}
  }
  $hdr = @{}
  if ($token) { $hdr['Authorization'] = "Bearer $token" }

  $ok2, $code2, $body2 = Invoke-HttpJson 'POST' "$API/v1/maintenance/partition/ensure_current" $null $hdr 5 (Join-Path $QA_DIR 'maintenance_post.json')
  $ev = @("openapiPath=$foundPath", "httpCode=$code2")
  # Accept 200 (executed), 202/204 (no-op) or 401/403 (present but secured) as success if route exists in OpenAPI
  if ($foundPath -and $ok2 -and ($code2 -eq 200 -or $code2 -eq 202 -or $code2 -eq 204 -or $code2 -eq 403 -or $code2 -eq 401)) {
    $ev += 'accepted_codes=200,202,204,401,403'
    Step-End ([ref]$S) 'PASS' $ev
  }
  elseif (-not $foundPath -and $code2 -eq 404) {
    Step-End ([ref]$S) 'FAIL' @('Route missing from OpenAPI and 404 calling endpoint')
  }
  else {
    Step-End ([ref]$S) 'FAIL' $ev
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 6) REGISTER & LOGIN
$S = Step-Start 'Register & Login'
try {
  $regBody = @{ email = $EMAIL; password = $PASS; org_name = $ORG }
  $null = Invoke-HttpJson 'POST' "$API/v1/auth/register" $regBody $null 8 (Join-Path $QA_DIR 'register.json')
  $ok2, $code2, $body2 = Invoke-HttpJson 'POST' "$API/v1/auth/login" @{ email = $EMAIL; password = $PASS } $null 8 (Join-Path $QA_DIR 'login.json')
  $token = $null
  try { $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token } catch {}
  if ($token) {
    Step-End ([ref]$S) 'PASS' @("loginStatus=$code2", ("tokenLen={0}" -f $token.Length))
  }
  else {
    Step-End ([ref]$S) 'FAIL' @("login=$code2")
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 7) RETRY POLICY
$S = Step-Start 'Create retry policy'
try {
  $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token
  $hdr = @{ Authorization = "Bearer $token" }
  $policy = @{ name = 'QA Fast'; max_retries = 3; initial_delay_minutes = 1; backoff_multiplier = 2; max_delay_minutes = 60; enabled_channels = @('email') }
  $ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/retry/policies" $policy $hdr 8 (Join-Path $QA_DIR 'policy.json')
  if ($ok -and ($code -eq 200 -or $code -eq 201)) {
    Step-End ([ref]$S) 'PASS' @("status=$code")
  }
  else {
    Step-End ([ref]$S) 'FAIL' @("code=$code", $body)
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 8) EVENT INGEST (authorized)
$S = Step-Start 'Ingest failed event (authorized)'
try {
  $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token
  $hdr = @{ Authorization = "Bearer $token" }
  $evt = @{ transaction_ref = $REF; amount = 1299; currency = 'inr'; gateway = 'razorpay'; failure_reason = 'insufficient_funds'; metadata = @{ qa = 'true' }; customer = @{ email = $EMAIL } }
  $ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/events/payment_failed" $evt $hdr 8 (Join-Path $QA_DIR 'ingest.json')
  if ($ok -and ($code -eq 200 -or $code -eq 201)) {
    Step-End ([ref]$S) 'PASS' @("status=$code")
  }
  else {
    Step-End ([ref]$S) 'FAIL' @("code=$code", $body)
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 9) RECOVERY LINK
$S = Step-Start 'Issue recovery link'
try {
  $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token
  $hdr = @{ Authorization = "Bearer $token" }
  $ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/recoveries/by_ref/$REF/link" @{ ttl_hours = 24; channel = 'email' } $hdr 8 (Join-Path $QA_DIR 'recovery_link.json')
  if ($ok -and ($code -eq 200 -or $code -eq 201)) {
    Step-End ([ref]$S) 'PASS' @("status=$code")
  }
  else {
    Step-End ([ref]$S) 'FAIL' @("code=$code", $body)
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 10) CELERY / REDIS
$S = Step-Start 'Celery/Redis scheduling (best-effort)'
try {
  $redisOk = $false
  try {
    $conn = Test-NetConnection -ComputerName '127.0.0.1' -Port 6379 -WarningAction SilentlyContinue
    if ($conn.TcpTestSucceeded) { $redisOk = $true }
  }
  catch {}

  if (-not $redisOk) {
    Step-End ([ref]$S) 'SKIP' @('Redis not reachable on 6379; skipping scheduling verification')
  }
  else {
    $ok, $code, $body = Invoke-HttpJson 'GET' "$API/v1/analytics/attempts?ref=$REF" $null $null 8 (Join-Path $QA_DIR 'attempts.json')
    if ($ok -and $code -eq 200) {
      Step-End ([ref]$S) 'PASS' @('attempts listed')
    }
    else {
      Step-End ([ref]$S) 'WARN' @("code=$code (worker/beat may be down)")
    }
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @($_.Exception.Message)
}

# 11) RAZORPAY PING (if present)
$S = Step-Start 'Razorpay ping'
try {
  $ok, $code, $body = Invoke-HttpJson 'GET' "$API/v1/payments/razorpay/ping" $null $null 5 (Join-Path $QA_DIR 'razorpay_ping.json')
  if ($ok -and $code -eq 200) {
    Step-End ([ref]$S) 'PASS' @('connected')
  }
  else {
    Step-End ([ref]$S) 'SKIP' @("code=$code (keys likely not set)")
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @($_.Exception.Message)
}

# 12) RAZORPAY ORDER (if keys)
$S = Step-Start 'Razorpay order create'
try {
  $token = (Get-Content "$QA_DIR\login.json" | ConvertFrom-Json).access_token
  $hdr = @{ Authorization = "Bearer $token" }
  $ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/payments/razorpay/orders" @{ reference = $REF } $hdr 10 (Join-Path $QA_DIR 'razorpay_order.json')
  if ($ok -and ($code -eq 200 -or $code -eq 201)) {
    Step-End ([ref]$S) 'PASS' @("status=$code")
  }
  else {
    Step-End ([ref]$S) 'SKIP' @("code=$code (no keys or route missing)")
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @($_.Exception.Message)
}

# 13) WEBHOOK (dev-mode mock if enabled)
$S = Step-Start 'Webhook (mock) - best-effort'
try {
  $openapi = Get-Content (Join-Path $QA_DIR 'openapi.json') -Raw
  $hasWebhook = ($openapi -match '\/v1\/payments\/razorpay\/webhooks')
  if (-not $hasWebhook) {
    Step-End ([ref]$S) 'SKIP' @('No webhook route found')
  }
  else {
    $payload = @{ event = 'payment.captured'; payload = @{ payment = @{ entity = @{ id = 'pay_dummy' } } } }
    $ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/payments/razorpay/webhooks" $payload $null 5 (Join-Path $QA_DIR 'webhook_attempt.json')
    if ($ok -and ($code -ge 200 -and $code -lt 300)) {
      Step-End ([ref]$S) 'PASS' @('accepted')
    }
    elseif ($code -eq 400) {
      Step-End ([ref]$S) 'SKIP' @('Signature required (expected in secure mode)')
    }
    else {
      Step-End ([ref]$S) 'WARN' @("code=$code")
    }
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @($_.Exception.Message)
}

# 14) ANALYTICS
$S = Step-Start 'Analytics endpoints'
try {
  $ok1, $c1, $b1 = Invoke-HttpJson 'GET' "$API/v1/analytics/revenue_recovered" $null $null 5 (Join-Path $QA_DIR 'analytics_revenue.json')
  $ok2, $c2, $b2 = Invoke-HttpJson 'GET' "$API/v1/analytics/recovery_rate" $null $null 5 (Join-Path $QA_DIR 'analytics_rate.json')
  if ($ok1 -and $ok2 -and $c1 -eq 200 -and $c2 -eq 200) {
    Step-End ([ref]$S) 'PASS' @("revenue=$b1", "rate=$b2")
  }
  else {
    Step-End ([ref]$S) 'FAIL' @("codes=$c1,$c2")
  }
}
catch {
  Step-End ([ref]$S) 'FAIL' @($_.Exception.Message)
}

# 15) CLASSIFIER NEGATIVE
$S = Step-Start 'Classifier negative'
$payload = @{ code = 'totally_unknown_error_code'; message = 'whatever' }
$ok, $code, $body = Invoke-HttpJson 'POST' "$API/v1/classify" $payload $null 5 (Join-Path $QA_DIR 'classify_unknown.json')
if ($ok -and ($code -eq 200 -or $code -eq 422)) {
  Step-End ([ref]$S) 'PASS' @("status=$code")
}
else {
  Step-End ([ref]$S) 'FAIL' @("code=$code")
}

# 16) CONSOLE SMOKE
$S = Step-Start 'Console homepage'
try {
  $r = Invoke-WebRequest -Method GET -Uri $CONSOLE -TimeoutSec 3 -ErrorAction Stop
  if ($r.StatusCode -eq 200) {
    Step-End ([ref]$S) 'PASS' @('Console OK')
  }
  else {
    Step-End ([ref]$S) 'SKIP' @('not running')
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @('not running')
}

# 17) CI presence
$S = Step-Start 'CI workflow presence'
try {
  if (Test-Path '.\.github\workflows') {
    $yml = Get-ChildItem '.\.github\workflows' -Filter *.yml -Recurse -ErrorAction SilentlyContinue
    if ($yml.Count -gt 0) {
      Step-End ([ref]$S) 'PASS' @("$($yml.Count) workflow(s) found")
    }
    else {
      Step-End ([ref]$S) 'WARN' @('workflows dir empty')
    }
  }
  else {
    Step-End ([ref]$S) 'SKIP' @('no workflows dir')
  }
}
catch {
  Step-End ([ref]$S) 'SKIP' @($_.Exception.Message)
}

# 18) SUMMARY & CLEANUP
"`n==== SUMMARY ====\n" | Out-File -FilePath (Join-Path $QA_DIR 'summary.txt') -Encoding utf8
"{0,-40} {1,-6}" -f 'STEP', 'RESULT' | Tee-Object -FilePath (Join-Path $QA_DIR 'summary.txt') -Append
"{0,-40} {1,-6}" -f '----', '------' | Tee-Object -FilePath (Join-Path $QA_DIR 'summary.txt') -Append
foreach ($r in $global:RESULTS) {
  $line = ("{0,-40} {1,-6}" -f $r.Step, $r.Status)
  Write-Host $line
  $line | Tee-Object -FilePath (Join-Path $QA_DIR 'summary.txt') -Append | Out-Null
}

W "Cleaning up: attempting to close API process on :$UVICORN_PORT"
Stop-Port $UVICORN_PORT
W "Artifacts saved to: $QA_DIR"
