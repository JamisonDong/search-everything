# Map a local-only domain name to this machine for the dashboard.
#   1. Let browsers bypass the system proxy for the domain (current user, no admin needed).
#   2. Add "127.0.0.1 <domain>" to the hosts file (asks for administrator permission once).
# Exit code 0: the domain is usable. Exit code 1: not configured, the caller falls back to 127.0.0.1.
# Keep this file ASCII-only: Windows PowerShell 5 reads BOM-less UTF-8 scripts as the ANSI code page.
param(
    [Parameter(Mandatory = $true)][string]$Domain,
    # Internal: set when the script re-launches itself elevated to edit the hosts file.
    [switch]$HostsOnly
)

$hostsPath = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$entryPattern = '^\s*127\.0\.0\.1\s+' + [regex]::Escape($Domain) + '(\s|$)'

function Test-HostsEntry {
    if (-not (Test-Path $hostsPath)) { return $false }
    return [bool](Select-String -Path $hostsPath -Pattern $entryPattern -Quiet)
}

if ($HostsOnly) {
    try {
        if (-not (Test-HostsEntry)) {
            Add-Content -Path $hostsPath -Value "`r`n127.0.0.1`t$Domain" -Encoding ASCII -ErrorAction Stop
        }
        exit 0
    } catch {
        exit 1
    }
}

# 1. Proxy bypass: with a system proxy enabled, browsers would otherwise send the fake domain to the proxy.
try {
    $key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    $current = (Get-ItemProperty -Path $key -Name ProxyOverride -ErrorAction SilentlyContinue).ProxyOverride
    $entries = @()
    if ($current) { $entries = @($current -split ';' | Where-Object { $_ -ne '' }) }
    if ($entries -notcontains $Domain) {
        Set-ItemProperty -Path $key -Name ProxyOverride -Value ((@($Domain) + $entries) -join ';')
    }
} catch {
    # Not fatal: without a system proxy the bypass list is irrelevant.
}

# 2. Hosts file mapping.
if (Test-HostsEntry) { exit 0 }

Write-Host "[*] Requesting administrator permission to add $Domain to the hosts file..."
try {
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-Domain', $Domain, '-HostsOnly')
    Start-Process -FilePath 'powershell.exe' -ArgumentList $argList -Verb RunAs -Wait -WindowStyle Hidden -ErrorAction Stop
} catch {
    # The user declined the UAC prompt.
    exit 1
}

if (Test-HostsEntry) {
    ipconfig /flushdns | Out-Null
    exit 0
}
exit 1
