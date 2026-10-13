[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ConfigurationPath,
    [string]$ApiKey
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "services\fabric-admin-mcp"
$schemaPath = Join-Path $root "config\client.parameters.schema.json"

$env:PYTHONPATH = Join-Path $root "src"
$configJson = python -c "import json; from fabric_sre.config import load_config; print(json.dumps(load_config(r'$ConfigurationPath', r'$schemaPath')))"
if ($LASTEXITCODE -ne 0) { throw "Configuration validation failed." }
$config = $configJson | ConvertFrom-Json

$SubscriptionId = $config.foundry.subscriptionId
$ResourceGroup = $config.foundry.resourceGroup
$Location = $config.foundry.fabricAdminMcp.location
$EnvironmentName = $config.foundry.fabricAdminMcp.environmentName
$AppName = $config.foundry.fabricAdminMcp.appName
$ManagedIdentityName = $config.foundry.fabricAdminMcp.managedIdentityName
$RegistryName = $config.foundry.fabricAdminMcp.registryName
$ServicePrincipalDisplayName = $config.foundry.fabricAdminMcp.servicePrincipalDisplayName
$AdminApiSecurityGroupName = $config.foundry.fabricAdminMcp.adminApiSecurityGroupName
$TenantId = $config.azure.tenantId
$CapacityMetricsModelId = $config.fabric.capacityMetrics.semanticModelId

az account set --subscription $SubscriptionId
if ($LASTEXITCODE -ne 0) { throw "Unable to select subscription '$SubscriptionId'." }

$appExists = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query name -o tsv 2>$null
if (-not $ApiKey -and $appExists) {
    $ApiKey = az containerapp secret list `
        --name $AppName `
        --resource-group $ResourceGroup `
        --show-values `
        --query "[?name=='mcp-api-key'].value | [0]" -o tsv
}
if (-not $ApiKey) {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $ApiKey = [Convert]::ToBase64String($bytes)
}

$applications = @(
    az ad app list --display-name $ServicePrincipalDisplayName -o json |
        ConvertFrom-Json
)
if ($applications.Count -gt 1) {
    throw "Multiple Entra applications are named '$ServicePrincipalDisplayName'."
}
if ($applications.Count -eq 0) {
    $application = az ad app create `
        --display-name $ServicePrincipalDisplayName `
        --sign-in-audience AzureADMyOrg `
        -o json | ConvertFrom-Json
}
else {
    $application = $applications[0]
}

$servicePrincipals = @(
    az ad sp list --filter "appId eq '$($application.appId)'" -o json |
        ConvertFrom-Json
)
if ($servicePrincipals.Count -eq 0) {
    $servicePrincipal = az ad sp create --id $application.appId -o json | ConvertFrom-Json
}
else {
    $servicePrincipal = $servicePrincipals[0]
}

$securityGroupId = az ad group show `
    --group $AdminApiSecurityGroupName `
    --query id -o tsv
$isGroupMember = $null
for ($attempt = 1; $attempt -le 3; $attempt++) {
    $memberCheck = az ad group member check `
        --group $securityGroupId `
        --member-id $servicePrincipal.id `
        --query value -o tsv 2>&1
    if ($LASTEXITCODE -eq 0) {
        $isGroupMember = $memberCheck
        break
    }
    if ($attempt -lt 3) {
        Start-Sleep -Seconds (2 * $attempt)
    }
}
if ($isGroupMember -ne "true") {
    $addMemberResult = az ad group member add `
        --group $securityGroupId `
        --member-id $servicePrincipal.id 2>&1
    if (
        $LASTEXITCODE -ne 0 -and
        $addMemberResult -notmatch "already exist"
    ) {
        throw "Unable to add the Admin reader service principal to '$AdminApiSecurityGroupName'."
    }
}

$FabricAdminClientSecret = $null
if ($appExists) {
    $FabricAdminClientSecret = az containerapp secret list `
        --name $AppName `
        --resource-group $ResourceGroup `
        --show-values `
        --query "[?name=='fabric-admin-client-secret'].value | [0]" -o tsv
}
if (-not $FabricAdminClientSecret) {
    $FabricAdminClientSecret = az ad app credential reset `
        --id $application.appId `
        --append `
        --display-name "Fabric Admin MCP" `
        --years 1 `
        --query password -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Unable to create the Admin reader credential." }
}

$environment = az containerapp env show `
    --name $EnvironmentName `
    --resource-group $ResourceGroup `
    --query name -o tsv 2>$null
if (-not $environment) {
    az containerapp env create `
        --name $EnvironmentName `
        --resource-group $ResourceGroup `
        --location $Location `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to create Container Apps environment." }
}

$identityId = az identity show `
    --name $ManagedIdentityName `
    --resource-group $ResourceGroup `
    --query id -o tsv
$clientId = az identity show `
    --name $ManagedIdentityName `
    --resource-group $ResourceGroup `
    --query clientId -o tsv

$registryId = az acr show `
    --name $RegistryName `
    --resource-group $ResourceGroup `
    --query id -o tsv 2>$null
if (-not $registryId) {
    az acr create `
        --name $RegistryName `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku Basic `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to create Azure Container Registry." }
    $registryId = az acr show `
        --name $RegistryName `
        --resource-group $ResourceGroup `
        --query id -o tsv
}
$loginServer = az acr show `
    --name $RegistryName `
    --resource-group $ResourceGroup `
    --query loginServer -o tsv

$tag = [DateTime]::UtcNow.ToString("yyyyMMddHHmmss")
$image = "$loginServer/fabric-admin-mcp:$tag"
$env:PYTHONUTF8 = "1"
az acr build `
    --registry $RegistryName `
    --resource-group $ResourceGroup `
    --image "fabric-admin-mcp:$tag" `
    --no-logs `
    $source
if ($LASTEXITCODE -ne 0) { throw "Container image build failed." }

$buildDeadline = (Get-Date).AddMinutes(15)
do {
    $imageDigest = az acr repository show `
        --name $RegistryName `
        --image "fabric-admin-mcp:$tag" `
        --query digest -o tsv 2>$null
    if ($imageDigest) { break }
    Start-Sleep -Seconds 10
} while ((Get-Date) -lt $buildDeadline)
if (-not $imageDigest) { throw "Container image build did not complete within 15 minutes." }

$principalId = az identity show `
    --name $ManagedIdentityName `
    --resource-group $ResourceGroup `
    --query principalId -o tsv
$pullAssignment = az role assignment list `
    --assignee-object-id $principalId `
    --scope $registryId `
    --role AcrPull `
    --query "[0].id" -o tsv
if (-not $pullAssignment) {
    az role assignment create `
        --assignee-object-id $principalId `
        --assignee-principal-type ServicePrincipal `
        --scope $registryId `
        --role AcrPull `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to grant AcrPull to the managed identity." }
}

if (-not $appExists) {
    az containerapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --environment $EnvironmentName `
        --image $image `
        --ingress external `
        --target-port 8000 `
        --min-replicas 1 `
        --user-assigned $identityId `
        --registry-server $loginServer `
        --registry-identity $identityId `
        --secrets `
            "mcp-api-key=$ApiKey" `
            "fabric-admin-client-secret=$FabricAdminClientSecret" `
        --env-vars `
            "AZURE_CLIENT_ID=$clientId" `
            "AZURE_TENANT_ID=$TenantId" `
            "FABRIC_ADMIN_CLIENT_ID=$($application.appId)" `
            "FABRIC_ADMIN_CLIENT_SECRET=secretref:fabric-admin-client-secret" `
            "FABRIC_CAPACITY_METRICS_MODEL_ID=$CapacityMetricsModelId" `
            "MCP_API_KEY=secretref:mcp-api-key" `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Container App creation failed." }
}
else {
    az containerapp identity assign `
        --name $AppName `
        --resource-group $ResourceGroup `
        --user-assigned $identityId `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to assign the managed identity." }

    az containerapp registry set `
        --name $AppName `
        --resource-group $ResourceGroup `
        --server $loginServer `
        --identity $identityId `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to configure the container registry." }

    az containerapp secret set `
        --name $AppName `
        --resource-group $ResourceGroup `
        --secrets `
            "mcp-api-key=$ApiKey" `
            "fabric-admin-client-secret=$FabricAdminClientSecret" `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to configure the MCP API key." }

    az containerapp update `
        --name $AppName `
        --resource-group $ResourceGroup `
        --image $image `
        --min-replicas 1 `
        --set-env-vars `
            "AZURE_CLIENT_ID=$clientId" `
            "AZURE_TENANT_ID=$TenantId" `
            "FABRIC_ADMIN_CLIENT_ID=$($application.appId)" `
            "FABRIC_ADMIN_CLIENT_SECRET=secretref:fabric-admin-client-secret" `
            "FABRIC_CAPACITY_METRICS_MODEL_ID=$CapacityMetricsModelId" `
            "MCP_API_KEY=secretref:mcp-api-key" `
        --output none
    if ($LASTEXITCODE -ne 0) { throw "Unable to update the Container App." }
}

$fqdn = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn -o tsv

az containerapp update `
    --name $AppName `
    --resource-group $ResourceGroup `
    --set-env-vars "MCP_ALLOWED_HOST=$fqdn" `
    --output none
if ($LASTEXITCODE -ne 0) { throw "Unable to configure the MCP allowed host." }

[pscustomobject]@{
    appName = $AppName
    endpoint = "https://$fqdn/mcp"
    health = "https://$fqdn/health"
    apiKeyConfigured = $true
    apiKeyHeader = "x-api-key"
    managedIdentityClientId = $clientId
    fabricAdminServicePrincipalClientId = $application.appId
} | ConvertTo-Json
