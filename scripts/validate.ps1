[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    & $Python -m pytest
    if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }

    & $Python -m ruff check src tests notebooks
    if ($LASTEXITCODE -ne 0) { throw "Ruff validation failed." }

    node scripts\generate-report.mjs
    if ($LASTEXITCODE -ne 0) { throw "Power BI report generation failed." }

    powerbi-report-author validate "powerbi\FabricSRE\fr\FabricSRE-fr.Report" --pretty
    if ($LASTEXITCODE -ne 0) { throw "French PBIR validation failed." }

    powerbi-report-author validate "powerbi\FabricSRE\en\FabricSRE-en.Report" --pretty
    if ($LASTEXITCODE -ne 0) { throw "English PBIR validation failed." }

    Get-Content "config\client.parameters.schema.json" -Raw | ConvertFrom-Json | Out-Null
    Get-Content "pipelines\daily-collection.pipeline.template.json" -Raw | ConvertFrom-Json | Out-Null
    Write-Host "Fabric SRE validation succeeded."
}
finally {
    Pop-Location
}

