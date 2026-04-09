param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$ServiceName = "credit-scoring-api",
    [string]$Region = "asia-southeast1",

    [ValidateSet("plan", "apply-10", "apply-30", "apply-50", "apply-100", "monitor")]
    [string]$Action = "plan",

    [string]$NewRevision = "",
    [string]$OldRevision = "",

    [int]$Hours = 24,
    [string]$ApiKey = "",
    [string]$ApiUrl = ""
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing required command: $Name"
    }
}

function Get-LatestRevisions {
    param(
        [string]$Service,
        [string]$SvcRegion
    )

    $list = gcloud run revisions list `
        --project $ProjectId `
        --service $Service `
        --region $SvcRegion `
        --sort-by="~metadata.creationTimestamp" `
        --format="value(metadata.name)"

    $revs = @($list | Where-Object { $_ -and $_.Trim().Length -gt 0 })
    return $revs
}

function Resolve-ServiceUrl {
    param(
        [string]$Service,
        [string]$SvcRegion
    )

    $url = gcloud run services describe $Service `
        --project $ProjectId `
        --region $SvcRegion `
        --format "value(status.url)"

    return "$url"
}

function Set-Traffic {
    param(
        [string]$Service,
        [string]$SvcRegion,
        [string]$OldRev,
        [string]$NewRev,
        [int]$NewPercent
    )

    if (-not $NewRev) {
        throw "New revision is empty. Cannot update traffic."
    }

    if (-not $OldRev -or $NewPercent -ge 100) {
        Write-Host "Applying 100% traffic to new revision: $NewRev"
        gcloud run services update-traffic $Service `
            --project $ProjectId `
            --region $SvcRegion `
            --to-revisions "$NewRev=100"
        return
    }

    $oldPercent = 100 - $NewPercent
    Write-Host "Applying traffic split: $OldRev=$oldPercent, $NewRev=$NewPercent"
    gcloud run services update-traffic $Service `
        --project $ProjectId `
        --region $SvcRegion `
        --to-revisions "$OldRev=$oldPercent,$NewRev=$NewPercent"
}

function Show-Plan {
    param(
        [string]$Service,
        [string]$SvcRegion,
        [string]$OldRev,
        [string]$NewRev,
        [string]$ServiceUrl
    )

    Write-Host "Project: $ProjectId"
    Write-Host "Region:  $SvcRegion"
    Write-Host "Service: $Service"
    Write-Host "URL:     $ServiceUrl"
    Write-Host "Old rev: $OldRev"
    Write-Host "New rev: $NewRev"
    Write-Host ""
    Write-Host "Canary steps:"
    Write-Host "  1) apply-10"
    Write-Host "  2) apply-30"
    Write-Host "  3) apply-50"
    Write-Host "  4) apply-100"
    Write-Host ""
    Write-Host "Monitoring endpoint: $ServiceUrl/api/student/monitoring/summary?hours=$Hours"
}

function Show-Monitoring {
    param(
        [string]$ServiceUrl,
        [int]$WindowHours,
        [string]$Key
    )

    if (-not $ServiceUrl) {
        throw "ApiUrl/Service URL is empty."
    }

    if (-not $Key) {
        throw "ApiKey is required for monitoring endpoint."
    }

    $uri = "$ServiceUrl/api/student/monitoring/summary?hours=$WindowHours"
    $headers = @{ "X-API-Key" = $Key }

    Write-Host "Calling: $uri"
    $resp = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
    $resp | ConvertTo-Json -Depth 6
}

Require-Command -Name "gcloud"

# Ensure commands run in intended project.
gcloud config set project $ProjectId | Out-Null

$resolvedUrl = if ($ApiUrl) { $ApiUrl.TrimEnd('/') } else { (Resolve-ServiceUrl -Service $ServiceName -SvcRegion $Region).TrimEnd('/') }

$allRevisions = Get-LatestRevisions -Service $ServiceName -SvcRegion $Region
if ($allRevisions.Count -eq 0) {
    throw "No revisions found for service '$ServiceName' in region '$Region'."
}

if (-not $NewRevision) {
    $NewRevision = $allRevisions[0]
}

if (-not $OldRevision) {
    $OldRevision = if ($allRevisions.Count -ge 2) { $allRevisions[1] } else { "" }
}

switch ($Action) {
    "plan" {
        Show-Plan -Service $ServiceName -SvcRegion $Region -OldRev $OldRevision -NewRev $NewRevision -ServiceUrl $resolvedUrl
    }
    "apply-10" {
        Set-Traffic -Service $ServiceName -SvcRegion $Region -OldRev $OldRevision -NewRev $NewRevision -NewPercent 10
    }
    "apply-30" {
        Set-Traffic -Service $ServiceName -SvcRegion $Region -OldRev $OldRevision -NewRev $NewRevision -NewPercent 30
    }
    "apply-50" {
        Set-Traffic -Service $ServiceName -SvcRegion $Region -OldRev $OldRevision -NewRev $NewRevision -NewPercent 50
    }
    "apply-100" {
        Set-Traffic -Service $ServiceName -SvcRegion $Region -OldRev $OldRevision -NewRev $NewRevision -NewPercent 100
    }
    "monitor" {
        Show-Monitoring -ServiceUrl $resolvedUrl -WindowHours $Hours -Key $ApiKey
    }
}
