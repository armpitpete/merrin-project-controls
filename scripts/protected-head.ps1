[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$ExpectedCommit,

    [string]$Remote = 'origin',

    [switch]$SkipRemoteCheck
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed:`n$output"
    }
    return ($output | Out-String).Trim()
}

try {
    $null = Invoke-Git rev-parse --git-dir

    $expected = $ExpectedCommit.ToLowerInvariant()
    $head = (Invoke-Git rev-parse HEAD).ToLowerInvariant()

    if ($head -ne $expected) {
        throw "HEAD mismatch. Expected $expected but found $head."
    }

    $status = Invoke-Git status --porcelain
    if ($status) {
        throw "Working tree is not clean:`n$status"
    }

    $branch = Invoke-Git branch --show-current
    if (-not $branch) {
        throw 'Detached HEAD is not allowed for a protected action.'
    }

    if (-not $SkipRemoteCheck) {
        $null = Invoke-Git fetch --quiet $Remote $branch
        $remoteHead = (Invoke-Git rev-parse "$Remote/$branch").ToLowerInvariant()

        if ($remoteHead -ne $expected) {
            throw "Remote head mismatch. Expected $expected but $Remote/$branch is $remoteHead."
        }
    }

    Write-Output "Protected head accepted: $expected on branch $branch."
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
