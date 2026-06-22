# ═══════════════════════════════════════════════════════════════════════════════
#  SignDecoder — Emoji API Test Suite
#  Usage: .\scripts\test_emoji_api.ps1
#         .\scripts\test_emoji_api.ps1 -BaseUrl "http://localhost:8000" -Verbose
# ═══════════════════════════════════════════════════════════════════════════════

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$Verbose
)

# ── Helpers ────────────────────────────────────────────────────────────────────

$PASS  = 0
$FAIL  = 0
$SKIP  = 0
$START = Get-Date

function Write-Header($text) {
    Write-Host ""
    Write-Host ("═" * 65) -ForegroundColor DarkGray
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host ("═" * 65) -ForegroundColor DarkGray
}

function Write-Section($text) {
    Write-Host ""
    Write-Host "  ── $text" -ForegroundColor Yellow
}

function Test-Case {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [int]$ExpectStatus = 200,
        [string]$ExpectField = $null,
        [string]$ExpectValue = $null,
        [switch]$ShouldFail
    )

    $t0 = Get-Date
    try {
        $params = @{ Uri = $Url; Method = $Method; TimeoutSec = 15 }
        if ($Body) {
            $params.Body        = ($Body | ConvertTo-Json -Depth 5)
            $params.ContentType = "application/json"
        }

        $resp = Invoke-RestMethod @params -ErrorAction Stop
        $ms   = [int]((Get-Date) - $t0).TotalMilliseconds

        if ($ShouldFail) {
            Fail $Name "Expected failure but got 2xx" $ms
            return
        }

        # Optional field assertion
        if ($ExpectField -and $ExpectValue) {
            $actual = $resp.$ExpectField
            if ("$actual" -ne $ExpectValue) {
                Fail $Name "Field '$ExpectField': expected '$ExpectValue', got '$actual'" $ms
                return
            }
        }

        Pass $Name $ms
        if ($Verbose) {
            Write-Host "     Response: $($resp | ConvertTo-Json -Depth 3 -Compress)" -ForegroundColor DarkGray
        }
        return $resp

    } catch [System.Net.WebException] {
        $ms = [int]((Get-Date) - $t0).TotalMilliseconds
        $statusCode = [int]$_.Exception.Response.StatusCode

        if ($ShouldFail -and $statusCode -eq $ExpectStatus) {
            Pass "$Name (expected $statusCode)" $ms
            if ($Verbose) { Write-Host "     Got expected error: $($_.Exception.Message)" -ForegroundColor DarkGray }
            return
        }
        Fail $Name "HTTP $statusCode — $($_.Exception.Message)" $ms

    } catch {
        $ms = [int]((Get-Date) - $t0).TotalMilliseconds
        if ($ShouldFail) {
            Pass "$Name (expected error)" $ms
            return
        }
        Fail $Name $_.Exception.Message $ms
    }
}

function Pass($name, $ms) {
    $script:PASS++
    Write-Host "  ✓ PASS  " -ForegroundColor Green -NoNewline
    Write-Host "$name " -NoNewline
    Write-Host "(${ms}ms)" -ForegroundColor DarkGray
}

function Fail($name, $reason, $ms) {
    $script:FAIL++
    Write-Host "  ✗ FAIL  " -ForegroundColor Red -NoNewline
    Write-Host "$name " -NoNewline
    Write-Host "(${ms}ms)" -ForegroundColor DarkGray
    Write-Host "          → $reason" -ForegroundColor Red
}

function Skip-Case($name, $reason) {
    $script:SKIP++
    Write-Host "  ⊘ SKIP  " -ForegroundColor DarkYellow -NoNewline
    Write-Host "$name — $reason" -ForegroundColor DarkGray
}

# ═══════════════════════════════════════════════════════════════════════════════
#  BEGIN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Header "SignDecoder API Test Suite"
Write-Host "  Base URL : $BaseUrl" -ForegroundColor Gray
Write-Host "  Started  : $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray

# ── 1. Health checks ────────────────────────────────────────────────────────

Write-Section "1. Health and Availability"

Test-Case -Name "GET /health — server is alive" `
    -Url "$BaseUrl/health"

Test-Case -Name "GET /health/live — liveness probe" `
    -Url "$BaseUrl/health/live" `
    -ExpectField "alive" -ExpectValue "True"

Test-Case -Name "GET /health/ready — readiness probe" `
    -Url "$BaseUrl/health/ready"

Test-Case -Name "GET / — root info endpoint" `
    -Url "$BaseUrl/"

# ── 2. Standard Translation ─────────────────────────────────────────────────

Write-Section "2. Standard Translation (POST /api/v1/translate)"

Test-Case -Name "Simple sentence" `
    -Url "$BaseUrl/api/v1/translate" -Method POST `
    -Body @{ text = "Sourav ate breakfast at home yesterday"; sign_language = "ISL"; include_details = $true }

Test-Case -Name "Short sentence" `
    -Url "$BaseUrl/api/v1/translate" -Method POST `
    -Body @{ text = "I go school"; sign_language = "ISL"; include_details = $false }

Test-Case -Name "Question sentence" `
    -Url "$BaseUrl/api/v1/translate" -Method POST `
    -Body @{ text = "Where is the hospital?"; sign_language = "ISL"; include_details = $true }

# ── 3. Emoji ML Endpoint — Happy Path ──────────────────────────────────────

Write-Section "3. Emoji ML (POST /api/convert-to-emoji) — Valid inputs"

$happyCases = @(
    @{ gloss = "I eat breakfast morning";       label = "meal gloss"    },
    @{ gloss = "she drink coffee daily";        label = "daily routine" },
    @{ gloss = "boy run school fast";           label = "action gloss"  },
    @{ gloss = "family celebrate birthday";     label = "event gloss"   },
    @{ gloss = "he read book night";            label = "leisure gloss" },
    @{ gloss = "rain fall heavy outside";       label = "weather gloss" },
    @{ gloss = "doctor help sick person";       label = "medical gloss" },
    @{ gloss = "yesterday home sourav breakfast eat"; label = "full ISL sentence" }
)

foreach ($c in $happyCases) {
    $result = Test-Case -Name "Convert: $($c.label)" `
        -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
        -Body @{ text = $c.gloss } `
        -ExpectField "success" -ExpectValue "True"

    if ($result -and $Verbose) {
        Write-Host "     Input : $($c.gloss)" -ForegroundColor DarkGray
        Write-Host "     Emoji : $($result.emoji)" -ForegroundColor Magenta
    }
}

# ── 4. Emoji ML Endpoint — Error Scenarios ─────────────────────────────────

Write-Section "4. Emoji ML — Error / Edge Cases"

Test-Case -Name "Empty string body → 422 Validation Error" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = "" } `
    -ExpectStatus 422 -ShouldFail

Test-Case -Name "Whitespace only → 422 Validation Error" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = "   " } `
    -ExpectStatus 422 -ShouldFail

Test-Case -Name "Missing 'text' field → 422 Validation Error" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ wrong_key = "hello" } `
    -ExpectStatus 422 -ShouldFail

Test-Case -Name "Very long input (500 chars)" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = ("word " * 100).Trim() }

Test-Case -Name "Single word input" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = "eat" }

Test-Case -Name "Numbers in gloss" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = "3 people eat food" }

Test-Case -Name "Mixed case input" `
    -Url "$BaseUrl/api/convert-to-emoji" -Method POST `
    -Body @{ text = "YESTERDAY HOME EAT FOOD" }

# ── 5. Performance / Load Tests ─────────────────────────────────────────────

Write-Section "5. Performance — Consecutive Requests"

Write-Host "  Running 5 consecutive requests..." -ForegroundColor Gray
$times = @()
for ($i = 1; $i -le 5; $i++) {
    $t0 = Get-Date
    try {
        $body = @{ text = "I eat breakfast morning" }
        $r = Invoke-RestMethod -Uri "$BaseUrl/api/convert-to-emoji" `
            -Method POST -ContentType "application/json" -Body ($body | ConvertTo-Json) -TimeoutSec 30
        $ms = [int]((Get-Date) - $t0).TotalMilliseconds
        $times += $ms
        Write-Host "     Request $i : ${ms}ms  → $($r.emoji)" -ForegroundColor DarkGray
        $script:PASS++
    } catch {
        $ms = [int]((Get-Date) - $t0).TotalMilliseconds
        Write-Host "     Request $i : FAILED (${ms}ms) — $($_.Exception.Message)" -ForegroundColor Red
        $script:FAIL++
    }
}
if ($times.Count -gt 0) {
    $avg = [int]($times | Measure-Object -Average).Average
    $min = ($times | Measure-Object -Minimum).Minimum
    $max = ($times | Measure-Object -Maximum).Maximum
    Write-Host "  ℹ Avg: ${avg}ms   Min: ${min}ms   Max: ${max}ms" -ForegroundColor Cyan
}

# ── 6. Batch conversion (manual multi-call) ─────────────────────────────────

Write-Section "6. Batch Gloss Conversion (display table)"

$batch = @(
    "I eat breakfast",
    "she drink coffee morning",
    "boy runs to school",
    "we celebrate birthday",
    "he is angry and fights",
    "family eats dinner together"
)

Write-Host ""
Write-Host ("  {0,-40} {1}" -f "GLOSS INPUT", "EMOJI OUTPUT") -ForegroundColor Yellow
Write-Host ("  " + "-" * 62) -ForegroundColor DarkGray

foreach ($g in $batch) {
    try {
        $body = @{ text = $g }
        $r    = Invoke-RestMethod -Uri "$BaseUrl/api/convert-to-emoji" `
                    -Method POST -ContentType "application/json" -Body ($body | ConvertTo-Json) -TimeoutSec 20
        $col1 = $g.PadRight(38).Substring(0, [Math]::Min($g.Length, 38))
        Write-Host ("  {0,-40} {1}" -f $col1, $r.emoji)
        $script:PASS++
    } catch {
        Write-Host ("  {0,-40} ERROR: {1}" -f $g, $_.Exception.Message) -ForegroundColor Red
        $script:FAIL++
    }
}

# ── 7. Swagger UI availability ──────────────────────────────────────────────

Write-Section "7. Documentation Endpoints"

Test-Case -Name "GET /docs — Swagger UI reachable" `
    -Url "$BaseUrl/docs"

Test-Case -Name "GET /redoc — ReDoc UI reachable" `
    -Url "$BaseUrl/redoc"

# ═══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

$elapsed = [int]((Get-Date) - $START).TotalSeconds
$total   = $PASS + $FAIL + $SKIP

Write-Host ""
Write-Host ("═" * 65) -ForegroundColor DarkGray
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host ("═" * 65) -ForegroundColor DarkGray
Write-Host "  Total    : $total tests in ${elapsed}s"

Write-Host "  " -NoNewline
Write-Host "Passed  : $PASS" -ForegroundColor Green -NoNewline
Write-Host "   " -NoNewline
Write-Host "Failed  : $FAIL" -ForegroundColor Red -NoNewline
Write-Host "   " -NoNewline
Write-Host "Skipped : $SKIP" -ForegroundColor DarkYellow
Write-Host ""

if ($FAIL -eq 0) {
    Write-Host "  ✦ All tests passed! API is healthy." -ForegroundColor Green
} else {
    Write-Host "  ✗ $FAIL test(s) failed. Check the backend logs for details." -ForegroundColor Red
    Write-Host "    Run: Get-Content backend/logs/signspeak.log -Tail 30" -ForegroundColor DarkGray
}
Write-Host ("═" * 65) -ForegroundColor DarkGray
Write-Host ""

# ── Quick-reference commands printed at end ──────────────────────────────────
Write-Host "  QUICK COMMANDS (copy-paste any):" -ForegroundColor Yellow
Write-Host "  # Single emoji test:" -ForegroundColor DarkGray
Write-Host '  Invoke-RestMethod -Uri "http://localhost:8000/api/convert-to-emoji" -Method POST -ContentType "application/json" -Body "{\"text\":\"I eat breakfast morning\"}" | ConvertTo-Json'
Write-Host ""
Write-Host "  # Health check:" -ForegroundColor DarkGray
Write-Host '  Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json'
Write-Host ""
Write-Host "  # Watch backend logs:" -ForegroundColor DarkGray
Write-Host '  Get-Content backend\logs\signspeak.log -Wait -Tail 20'
Write-Host ""
