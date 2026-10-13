[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$ConfigurationPath,
    [switch]$CreateWorkspace
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$schemaPath = Join-Path $root "config\client.parameters.schema.json"

if (-not (Test-Path $ConfigurationPath)) {
    throw "Configuration file not found: $ConfigurationPath"
}

$env:PYTHONPATH = Join-Path $root "src"
$configJson = python -c "import json; from fabric_sre.config import load_config; print(json.dumps(load_config(r'$ConfigurationPath', r'$schemaPath')))"
if ($LASTEXITCODE -ne 0) { throw "Configuration validation failed." }
$config = $configJson | ConvertFrom-Json

$accounts = az account list --all -o json | ConvertFrom-Json
foreach ($subscriptionId in $config.azure.subscriptionIds) {
    if (-not ($accounts | Where-Object id -eq $subscriptionId)) {
        throw "Subscription '$subscriptionId' is not visible to the active Azure CLI account. Refusing to deploy."
    }
}

$headers = "x-ms-fabric-skill=fabric-sre-accelerator"
$workspaceName = $config.fabric.adminWorkspaceName
$workspaces = az rest `
    --method get `
    --resource "https://api.fabric.microsoft.com" `
    --url "https://api.fabric.microsoft.com/v1/workspaces" `
    --headers $headers -o json | ConvertFrom-Json
$workspace = @($workspaces.value | Where-Object displayName -eq $workspaceName)

if ($workspace.Count -gt 1) {
    throw "Multiple Fabric workspaces are named '$workspaceName'. Resolve the ambiguity before deployment."
}
if ($workspace.Count -eq 0) {
    if (-not $CreateWorkspace) {
        throw "Workspace '$workspaceName' does not exist. Re-run with -CreateWorkspace after selecting the intended capacity in the client configuration."
    }
    if (-not $PSCmdlet.ShouldProcess($workspaceName, "Create Fabric administration workspace")) {
        return
    }
    $body = @{ displayName = $workspaceName; description = "Fabric SRE administration workspace" } | ConvertTo-Json
    $workspace = az rest `
        --method post `
        --resource "https://api.fabric.microsoft.com" `
        --url "https://api.fabric.microsoft.com/v1/workspaces" `
        --headers $headers "Content-Type=application/json" `
        --body $body -o json | ConvertFrom-Json
}
else {
    $workspace = $workspace[0]
}

$items = az rest `
    --method get `
    --resource "https://api.fabric.microsoft.com" `
    --url "https://api.fabric.microsoft.com/v1/workspaces/$($workspace.id)/items" `
    --headers $headers -o json | ConvertFrom-Json
$lakehouse = @($items.value | Where-Object {
    $_.displayName -eq $config.fabric.lakehouseName -and $_.type -eq "Lakehouse"
})
if ($lakehouse.Count -eq 0 -and $PSCmdlet.ShouldProcess($config.fabric.lakehouseName, "Create Lakehouse")) {
    $body = @{
        displayName = $config.fabric.lakehouseName
        type = "Lakehouse"
        description = "Historical Fabric administration telemetry"
    } | ConvertTo-Json
    az rest `
        --method post `
        --resource "https://api.fabric.microsoft.com" `
        --url "https://api.fabric.microsoft.com/v1/workspaces/$($workspace.id)/items" `
        --headers $headers "Content-Type=application/json" `
        --body $body -o json | Out-Null
}

$plan = [ordered]@{
    workspaceName = $workspaceName
    workspaceId = $workspace.id
    lakehouseName = $config.fabric.lakehouseName
    semanticModelName = $config.fabric.semanticModelName
    frenchReport = $config.fabric.reportNameFr
    englishReport = $config.fabric.reportNameEn
    sourceRoot = $root
    next = @(
        "Upload config, src, notebooks, and queries to the Lakehouse Files/fabric-sre path.",
        "Create notebooks and pipeline from the versioned assets.",
        "Run bootstrap, collection, and gold build.",
        "Set TMDL Server and Database parameters, then publish the semantic model.",
        "Publish both PBIR reports and bind them to the semantic model.",
        "Apply agent instructions and routines after the Foundry target subscription is visible."
    )
}
$plan | ConvertTo-Json -Depth 5

