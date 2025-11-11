# Azure Static Web Apps Deployment Script
# Make sure you're logged in: az login
# Make sure you have the correct subscription: az account show

Write-Host "=== Azure Static Web Apps Deployment ===" -ForegroundColor Green
Write-Host ""

# Configuration
$resourceGroupName = "stealth-tinko-prod-rg"
$swaName = "stealth-tinko-swa"
$location = "eastus"
$sku = "Free"
$githubRepo = "https://github.com/stealthorga-crypto/STEALTH-TINKO"
$githubBranch = "main"

# Check if logged in
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show --query "user.name" -o tsv 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}
Write-Host "Logged in as: $account" -ForegroundColor Green
Write-Host ""

# Check resource group exists
Write-Host "Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroupName
if ($rgExists -eq "false") {
    Write-Host "Resource group $resourceGroupName does not exist. Creating..." -ForegroundColor Yellow
    az group create --name $resourceGroupName --location $location
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create resource group" -ForegroundColor Red
        exit 1
    }
    Write-Host "Resource group created successfully" -ForegroundColor Green
} else {
    Write-Host "Resource group $resourceGroupName exists" -ForegroundColor Green
}
Write-Host ""

# Create Static Web App
Write-Host "Creating Azure Static Web App..." -ForegroundColor Yellow
Write-Host "Name: $swaName" -ForegroundColor Cyan
Write-Host "Resource Group: $resourceGroupName" -ForegroundColor Cyan
Write-Host "Location: $location" -ForegroundColor Cyan
Write-Host "SKU: $sku" -ForegroundColor Cyan
Write-Host ""

# Check if SWA already exists
az staticwebapp show --name $swaName --resource-group $resourceGroupName --query "id" -o tsv 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Static Web App $swaName already exists" -ForegroundColor Yellow
    $choice = Read-Host "Do you want to continue and update the existing SWA? (y/N)"
    if ($choice -ne "y" -and $choice -ne "Y") {
        Write-Host "Deployment cancelled" -ForegroundColor Yellow
        exit 0
    }
} else {
    # Create the SWA
    Write-Host "Creating new Static Web App..." -ForegroundColor Yellow
    az staticwebapp create `
        --name $swaName `
        --resource-group $resourceGroupName `
        --source $githubRepo `
        --location $location `
        --branch $githubBranch `
        --app-location "/tinko-console" `
        --api-location "/api" `
        --output-location "out" `
        --sku $sku
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create Static Web App" -ForegroundColor Red
        exit 1
    }
}

# Get deployment token
Write-Host ""
Write-Host "Getting deployment token..." -ForegroundColor Yellow
$deploymentToken = az staticwebapp secrets list --name $swaName --resource-group $resourceGroupName --query "properties.apiKey" -o tsv

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($deploymentToken)) {
    Write-Host "Failed to get deployment token" -ForegroundColor Red
    exit 1
}

Write-Host "Deployment token retrieved successfully" -ForegroundColor Green
Write-Host ""

# Get SWA details
Write-Host "Static Web App Details:" -ForegroundColor Green
$swaDetails = az staticwebapp show --name $swaName --resource-group $resourceGroupName --query "{hostname:defaultHostname,resourceId:id,location:location}" -o table
Write-Host $swaDetails

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Add the deployment token to your GitHub repository secrets:"
Write-Host "   Secret Name: AZURE_STATIC_WEB_APPS_API_TOKEN"
Write-Host "   Secret Value: $deploymentToken" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Add JWT secret to GitHub repository secrets:"
Write-Host "   Secret Name: JWT_SECRET"
Write-Host "   Secret Value: your-super-secret-jwt-key" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Update the GitHub repository URL in this script (line 8)"
Write-Host ""
Write-Host "4. Push changes to trigger the GitHub Actions workflow"
Write-Host ""
Write-Host "5. Your Static Web App will be available at:" -ForegroundColor Green
$hostname = az staticwebapp show --name $swaName --resource-group $resourceGroupName --query "defaultHostname" -o tsv
Write-Host "   https://$hostname" -ForegroundColor Cyan
Write-Host ""

# Additional configuration
Write-Host "=== Additional Configuration ===" -ForegroundColor Green
Write-Host "To configure custom domains, authentication providers, and other settings:"
Write-Host "Visit: https://portal.azure.com/#resource/subscriptions/$(az account show --query 'id' -o tsv)/resourceGroups/$resourceGroupName/providers/Microsoft.Web/staticSites/$swaName/overview"
Write-Host ""
Write-Host "Deployment script completed successfully!" -ForegroundColor Green