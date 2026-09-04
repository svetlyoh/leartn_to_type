$ErrorActionPreference = 'Stop'

function Read-PlainPin([string]$Prompt) {
    $secure = Read-Host $Prompt -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}

$sitePin = Read-PlainPin 'Site PIN (6-12 digits)'
$adminPin = Read-PlainPin 'Admin PIN (8-12 digits)'

if ($sitePin -notmatch '^\d{6,12}$') {
    throw 'The site PIN must contain 6-12 digits.'
}
if ($adminPin -notmatch '^\d{8,12}$') {
    throw 'The admin PIN must contain 8-12 digits.'
}
if ($sitePin -eq $adminPin) {
    throw 'Use different site and admin PINs.'
}

$tokenBytes = New-Object byte[] 48
$random = [Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $random.GetBytes($tokenBytes)
}
finally {
    $random.Dispose()
}
$bootstrapToken = -join ($tokenBytes | ForEach-Object { $_.ToString('x2') })

try {
    $bootstrapToken | npx wrangler secret put BOOTSTRAP_TOKEN --name leartn-to-type
    if ($LASTEXITCODE -ne 0) { throw 'Could not configure the temporary bootstrap secret.' }

    $headers = @{ Authorization = "Bearer $bootstrapToken" }
    $body = @{ site_pin = $sitePin; admin_pin = $adminPin } | ConvertTo-Json -Compress
    $result = $null
    for ($attempt = 1; $attempt -le 4; $attempt++) {
        try {
            $result = Invoke-RestMethod -Method Post -Uri 'https://leartn-to-type.svetlyoh.workers.dev/api/v1/admin/bootstrap' -Headers $headers -ContentType 'application/json' -Body $body
            break
        }
        catch {
            $status = [int]$_.Exception.Response.StatusCode
            if ($status -ne 401 -or $attempt -eq 4) { throw }
            Write-Host 'Waiting for the temporary Worker secret to propagate...'
            Start-Sleep -Seconds 8
        }
    }
    if (-not $result.ok) { throw 'Bootstrap did not complete.' }
    Write-Host 'Cadence bootstrap completed successfully.' -ForegroundColor Green
}
finally {
    $sitePin = $null
    $adminPin = $null
    $bootstrapToken = $null
    'y' | npx wrangler secret delete BOOTSTRAP_TOKEN --name leartn-to-type
}
