[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SubscriptionId,
    [Parameter(Mandatory)]
    [string]$ResourceGroup,
    [Parameter(Mandatory)]
    [string]$AgentName,
    [string]$ExpectedAccount
)

$ErrorActionPreference = "Stop"
$account = az account show -o json | ConvertFrom-Json
if ($ExpectedAccount -and $account.user.name -ne $ExpectedAccount) {
    throw "The active Azure CLI account is '$($account.user.name)', not '$ExpectedAccount'."
}
$subscriptions = az account list --all -o json | ConvertFrom-Json
if (-not ($subscriptions | Where-Object id -eq $SubscriptionId)) {
    throw "Subscription '$SubscriptionId' is not visible to '$($account.user.name)'."
}
$resource = az resource list `
    --subscription $SubscriptionId `
    --resource-group $ResourceGroup `
    --query "[?name=='$AgentName']" -o json | ConvertFrom-Json
if (-not $resource) {
    throw "Agent/resource '$AgentName' was not found in resource group '$ResourceGroup'."
}
$resource | ConvertTo-Json -Depth 10
