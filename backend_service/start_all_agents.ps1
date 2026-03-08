<#
.SYNOPSIS
    Start all TheOrchestrator agents and the main API server in separate Windows Terminal tabs.

.DESCRIPTION
    Opens 12 tabs in the current Windows Terminal window:
      - Tab 1:  Main FastAPI server (port 8000)
      - Tab 2:  Job Search Assistant (port 8001)
      - Tab 3:  GitHub Assistant (port 8002)
      - Tab 4:  Filesystem Assistant (port 8003)
      - Tab 5:  Web Research Assistant (port 8004)
      - Tab 6:  Knowledge Manager (port 8005)
      - Tab 7:  Database Analyst (port 8006)
      - Tab 8:  Reasoning Assistant (port 8007)
      - Tab 9:  Browser Automation (port 8008)
      - Tab 10: Git Assistant (port 8009)
      - Tab 11: Time Assistant (port 8010)
      - Tab 12: Report Writer (port 8011)

.NOTES
    Requires Windows Terminal (wt.exe).
    Run this script from the project root: D:\projects\TheOrchestrator\backend_service
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = "D:\projects\TheOrchestrator\backend_service"
$HelperScript = Join-Path $PSScriptRoot "start_one_service.ps1"

if (-not (Get-Command wt.exe -ErrorAction SilentlyContinue)) {
    throw "Windows Terminal (wt.exe) was not found in PATH. Install Windows Terminal or add wt.exe to PATH."
}

if (-not (Test-Path $HelperScript)) {
    throw "Helper script not found: $HelperScript"
}

# Define all services: Title, UvicornAppPath, Port
$Services = @(
    [pscustomobject]@{ Title = "Orchestrator API (8000)";     AppPath = "app.main:app";                                    Port = 8000 },
    [pscustomobject]@{ Title = "Job Search (8001)";           AppPath = "app.agentic.job_search.agent:a2a_app";            Port = 8001 },
    [pscustomobject]@{ Title = "GitHub Assistant (8002)";     AppPath = "app.agentic.github_assistant.agent:a2a_app";       Port = 8002 },
    [pscustomobject]@{ Title = "Filesystem Assistant (8003)"; AppPath = "app.agentic.filesystem_assistant.agent:a2a_app";   Port = 8003 },
    [pscustomobject]@{ Title = "Web Research (8004)";         AppPath = "app.agentic.web_research_assistant.agent:a2a_app"; Port = 8004 },
    [pscustomobject]@{ Title = "Knowledge Manager (8005)";    AppPath = "app.agentic.knowledge_manager.agent:a2a_app";      Port = 8005 },
    [pscustomobject]@{ Title = "Database Analyst (8006)";     AppPath = "app.agentic.database_analyst.agent:a2a_app";       Port = 8006 },
    [pscustomobject]@{ Title = "Reasoning Assistant (8007)";  AppPath = "app.agentic.reasoning_assistant.agent:a2a_app";    Port = 8007 },
    [pscustomobject]@{ Title = "Browser Automation (8008)";   AppPath = "app.agentic.browser_automation.agent:a2a_app";     Port = 8008 },
    [pscustomobject]@{ Title = "Git Assistant (8009)";        AppPath = "app.agentic.git_assistant.agent:a2a_app";          Port = 8009 },
    [pscustomobject]@{ Title = "Time Assistant (8010)";       AppPath = "app.agentic.time_assistant.agent:a2a_app";         Port = 8010 },
    [pscustomobject]@{ Title = "Report Writer (8011)";        AppPath = "app.agentic.report_writer.agent:a2a_app";          Port = 8011 }
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " TheOrchestrator - Starting All Agents" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($svc in $Services) {
    Write-Host "  Starting: $($svc.Title)" -ForegroundColor Green

    $arguments = @(
        '-w',
        '0',
        'new-tab',
        '--title',
        $svc.Title,
        'powershell.exe',
        '-NoExit',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        $HelperScript,
        '-ProjectRoot',
        $ProjectRoot,
        '-AppPath',
        $svc.AppPath,
        '-Port',
        "$($svc.Port)"
    )

    & wt.exe @arguments

    # Small delay to avoid overwhelming the terminal
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " All 12 services launched!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Main API:            http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Job Search:          http://127.0.0.1:8001" -ForegroundColor Yellow
Write-Host "  GitHub Assistant:    http://127.0.0.1:8002" -ForegroundColor Yellow
Write-Host "  Filesystem:          http://127.0.0.1:8003" -ForegroundColor Yellow
Write-Host "  Web Research:        http://127.0.0.1:8004" -ForegroundColor Yellow
Write-Host "  Knowledge Manager:   http://127.0.0.1:8005" -ForegroundColor Yellow
Write-Host "  Database Analyst:    http://127.0.0.1:8006" -ForegroundColor Yellow
Write-Host "  Reasoning:           http://127.0.0.1:8007" -ForegroundColor Yellow
Write-Host "  Browser Automation:  http://127.0.0.1:8008" -ForegroundColor Yellow
Write-Host "  Git Assistant:       http://127.0.0.1:8009" -ForegroundColor Yellow
Write-Host "  Time Assistant:      http://127.0.0.1:8010" -ForegroundColor Yellow
Write-Host "  Report Writer:       http://127.0.0.1:8011" -ForegroundColor Yellow
Write-Host ""
