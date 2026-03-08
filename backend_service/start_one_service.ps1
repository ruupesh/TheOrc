param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$AppPath,

    [Parameter(Mandatory = $true)]
    [int]$Port,

    [Parameter()]
    [string]$HostName = "localhost"
)

$ErrorActionPreference = "Stop"

D:
& "$ProjectRoot\venv\Scripts\Activate.ps1"
Set-Location $ProjectRoot

Write-Host "Starting $AppPath on http://$HostName`:$Port" -ForegroundColor Cyan
uvicorn $AppPath --host $HostName --port $Port