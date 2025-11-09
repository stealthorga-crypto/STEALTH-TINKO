# STEALTH-TINKO Azure Deployment Script
# PowerShell script to deploy the application to Azure

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "stealth-tinko-$Environment-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipInfrastructure = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($message) { Write-ColorOutput Green $message }
function Write-Warning($message) { Write-ColorOutput Yellow $message }
function Write-Error($message) { Write-ColorOutput Red $message }
function Write-Info($message) { Write-ColorOutput Cyan $message }

# Main deployment function
function Deploy-StealthTinko {
    Write-Info "============================================"
    Write-Info "STEALTH-TINKO Azure Deployment ($Environment)"
    Write-Info "============================================"
    
    # Validate prerequisites
    Test-Prerequisites
    
    # Set Azure context
    Set-AzureContext
    
    # Create resource group if it doesn't exist
    New-ResourceGroupIfNotExists
    
    # Deploy infrastructure if not skipped
    if (-not $SkipInfrastructure) {
        Deploy-Infrastructure
    }
    
    # Deploy application
    Deploy-Application
    
    # Run post-deployment tasks
    Run-PostDeploymentTasks
    
    Write-Success "Deployment completed successfully!"
    Write-Info "Application URL: https://stealth-tinko-$Environment-app.azurewebsites.net"
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check if Azure CLI is installed
    try {
        $azVersion = az version --output tsv --query '"azure-cli"'
        Write-Success "✓ Azure CLI version: $azVersion"
    } catch {
        Write-Error "✗ Azure CLI is not installed or not in PATH"
        Write-Info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    }
    
    # Check if logged in to Azure
    try {
        $account = az account show --query 'name' --output tsv
        Write-Success "✓ Logged in to Azure account: $account"
    } catch {
        Write-Error "✗ Not logged in to Azure"
        Write-Info "Please run: az login"
        exit 1
    }
    
    # Check if Bicep is installed
    try {
        $bicepVersion = az bicep version --output tsv
        Write-Success "✓ Bicep version: $bicepVersion"
    } catch {
        Write-Warning "⚠ Bicep not found, installing..."
        az bicep install
        Write-Success "✓ Bicep installed"
    }
    
    # Check if required files exist
    $requiredFiles = @(
        "infra/azure/main.bicep",
        "infra/azure/parameters.$Environment.json",
        "requirements-azure.txt",
        "startup.py"
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "✓ Found: $file"
        } else {
            Write-Error "✗ Missing required file: $file"
            exit 1
        }
    }
}

function Set-AzureContext {
    Write-Info "Setting Azure context..."
    
    # Set subscription
    az account set --subscription $SubscriptionId
    Write-Success "✓ Set subscription: $SubscriptionId"
    
    # Register required resource providers
    $providers = @(
        "Microsoft.Web",
        "Microsoft.DBforPostgreSQL",
        "Microsoft.KeyVault",
        "Microsoft.Storage",
        "Microsoft.Communication",
        "Microsoft.Insights",
        "Microsoft.OperationalInsights"
    )
    
    foreach ($provider in $providers) {
        Write-Info "Registering provider: $provider"
        az provider register --namespace $provider --wait
    }
    Write-Success "✓ Resource providers registered"
}

function New-ResourceGroupIfNotExists {
    Write-Info "Checking resource group: $ResourceGroupName"
    
    $rgExists = az group exists --name $ResourceGroupName
    if ($rgExists -eq "false") {
        Write-Info "Creating resource group: $ResourceGroupName"
        if ($DryRun) {
            Write-Warning "[DRY RUN] Would create resource group: $ResourceGroupName in $Location"
        } else {
            az group create --name $ResourceGroupName --location $Location
            Write-Success "✓ Resource group created: $ResourceGroupName"
        }
    } else {
        Write-Success "✓ Resource group exists: $ResourceGroupName"
    }
}

function Deploy-Infrastructure {
    Write-Info "Deploying Azure infrastructure..."
    
    $deploymentName = "stealth-tinko-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    $templateFile = "infra/azure/main.bicep"
    $parametersFile = "infra/azure/parameters.$Environment.json"
    
    if ($DryRun) {
        Write-Warning "[DRY RUN] Would deploy infrastructure with:"
        Write-Info "  Template: $templateFile"
        Write-Info "  Parameters: $parametersFile"
        Write-Info "  Deployment: $deploymentName"
        
        # Run what-if analysis
        Write-Info "Running what-if analysis..."
        az deployment group what-if `
            --resource-group $ResourceGroupName `
            --template-file $templateFile `
            --parameters @$parametersFile
    } else {
        # Validate deployment first
        Write-Info "Validating deployment..."
        az deployment group validate `
            --resource-group $ResourceGroupName `
            --template-file $templateFile `
            --parameters @$parametersFile
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Deployment validation failed"
            exit 1
        }
        Write-Success "✓ Deployment validation passed"
        
        # Deploy infrastructure
        Write-Info "Deploying infrastructure..."
        az deployment group create `
            --resource-group $ResourceGroupName `
            --name $deploymentName `
            --template-file $templateFile `
            --parameters @$parametersFile `
            --verbose
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Infrastructure deployment failed"
            exit 1
        }
        Write-Success "✓ Infrastructure deployed successfully"
    }
}

function Deploy-Application {
    Write-Info "Deploying application..."
    
    $webAppName = "stealth-tinko-$Environment-app"
    
    if ($DryRun) {
        Write-Warning "[DRY RUN] Would deploy application to: $webAppName"
        return
    }
    
    # Create deployment package
    Write-Info "Creating deployment package..."
    $tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
    
    try {
        # Copy application files
        $filesToCopy = @(
            "app/*",
            "migrations/*",
            "models/*",
            "services/*",
            "schemas/*",
            "tasks/*",
            "requirements-azure.txt",
            "startup.py",
            "alembic.ini"
        )
        
        foreach ($pattern in $filesToCopy) {
            $files = Get-ChildItem -Path $pattern -Recurse -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $relativePath = Resolve-Path $file.FullName -Relative
                $destPath = Join-Path $tempDir $relativePath
                $destDir = Split-Path $destPath -Parent
                if (!(Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item $file.FullName $destPath -Force
            }
        }
        
        # Create zip package
        $zipPath = "$PWD/deployment-package.zip"
        if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
        
        Compress-Archive -Path "$tempDir/*" -DestinationPath $zipPath
        Write-Success "✓ Deployment package created: $zipPath"
        
        # Deploy to App Service
        Write-Info "Uploading to App Service..."
        az webapp deployment source config-zip `
            --resource-group $ResourceGroupName `
            --name $webAppName `
            --src $zipPath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Application deployment failed"
            exit 1
        }
        Write-Success "✓ Application deployed successfully"
        
        # Clean up
        Remove-Item $zipPath -Force
    } finally {
        Remove-Item $tempDir -Recurse -Force
    }
}

function Run-PostDeploymentTasks {
    Write-Info "Running post-deployment tasks..."
    
    $webAppName = "stealth-tinko-$Environment-app"
    
    if ($DryRun) {
        Write-Warning "[DRY RUN] Would run post-deployment tasks"
        return
    }
    
    # Wait for deployment to complete
    Write-Info "Waiting for application to start..."
    Start-Sleep -Seconds 30
    
    # Test application health
    $appUrl = "https://$webAppName.azurewebsites.net"
    $healthUrl = "$appUrl/health"
    
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 30
        Write-Success "✓ Application health check passed"
        Write-Info "Response: $($response | ConvertTo-Json -Compress)"
    } catch {
        Write-Warning "⚠ Health check failed, but deployment may still be successful"
        Write-Info "Check application logs for details"
    }
    
    # Show deployment summary
    Write-Info "============================================"
    Write-Info "DEPLOYMENT SUMMARY"
    Write-Info "============================================"
    Write-Info "Environment: $Environment"
    Write-Info "Resource Group: $ResourceGroupName"
    Write-Info "Application URL: $appUrl"
    Write-Info "Health Check URL: $healthUrl"
    Write-Info "============================================"
}

# Main execution
try {
    Deploy-StealthTinko
} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Info "Check the Azure portal for more details: https://portal.azure.com"
    exit 1
}