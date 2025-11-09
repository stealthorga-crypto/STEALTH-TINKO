#!/bin/bash

# STEALTH-TINKO Azure Deployment Script (Bash version)
# Cross-platform deployment script for Unix/Linux/macOS

set -euo pipefail

# Default values
ENVIRONMENT=""
SUBSCRIPTION_ID=""
RESOURCE_GROUP_NAME=""
LOCATION="East US"
SKIP_INFRASTRUCTURE=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage function
usage() {
    cat << EOF
Usage: $0 -e ENVIRONMENT -s SUBSCRIPTION_ID [OPTIONS]

Required:
    -e, --environment ENVIRONMENT    Environment (dev, staging, prod)
    -s, --subscription SUBSCRIPTION  Azure subscription ID

Optional:
    -g, --resource-group GROUP       Resource group name (default: stealth-tinko-ENV-rg)
    -l, --location LOCATION          Azure location (default: East US)
    -i, --skip-infrastructure        Skip infrastructure deployment
    -d, --dry-run                    Show what would be done without executing
    -h, --help                       Show this help

Examples:
    $0 -e dev -s 12345678-1234-1234-1234-123456789012
    $0 -e prod -s 12345678-1234-1234-1234-123456789012 --skip-infrastructure
    $0 -e dev -s 12345678-1234-1234-1234-123456789012 --dry-run

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--subscription)
            SUBSCRIPTION_ID="$2"
            shift 2
            ;;
        -g|--resource-group)
            RESOURCE_GROUP_NAME="$2"
            shift 2
            ;;
        -l|--location)
            LOCATION="$2"
            shift 2
            ;;
        -i|--skip-infrastructure)
            SKIP_INFRASTRUCTURE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$ENVIRONMENT" || -z "$SUBSCRIPTION_ID" ]]; then
    log_error "Environment and subscription ID are required"
    usage
    exit 1
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Environment must be one of: dev, staging, prod"
    exit 1
fi

# Set default resource group name if not provided
if [[ -z "$RESOURCE_GROUP_NAME" ]]; then
    RESOURCE_GROUP_NAME="stealth-tinko-${ENVIRONMENT}-rg"
fi

# Main deployment function
deploy_stealth_tinko() {
    log_info "============================================"
    log_info "STEALTH-TINKO Azure Deployment ($ENVIRONMENT)"
    log_info "============================================"
    
    # Validate prerequisites
    test_prerequisites
    
    # Set Azure context
    set_azure_context
    
    # Create resource group if it doesn't exist
    create_resource_group_if_not_exists
    
    # Deploy infrastructure if not skipped
    if [[ "$SKIP_INFRASTRUCTURE" == "false" ]]; then
        deploy_infrastructure
    fi
    
    # Deploy application
    deploy_application
    
    # Run post-deployment tasks
    run_post_deployment_tasks
    
    log_success "Deployment completed successfully!"
    log_info "Application URL: https://stealth-tinko-${ENVIRONMENT}-app.azurewebsites.net"
}

test_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Azure CLI is installed
    if command -v az &> /dev/null; then
        local az_version=$(az version --query '"azure-cli"' --output tsv)
        log_success "✓ Azure CLI version: $az_version"
    else
        log_error "✗ Azure CLI is not installed"
        log_info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check if logged in to Azure
    if az account show &> /dev/null; then
        local account=$(az account show --query 'name' --output tsv)
        log_success "✓ Logged in to Azure account: $account"
    else
        log_error "✗ Not logged in to Azure"
        log_info "Please run: az login"
        exit 1
    fi
    
    # Check if Bicep is installed
    if az bicep version &> /dev/null; then
        local bicep_version=$(az bicep version --output tsv)
        log_success "✓ Bicep version: $bicep_version"
    else
        log_warning "⚠ Bicep not found, installing..."
        az bicep install
        log_success "✓ Bicep installed"
    fi
    
    # Check if required files exist
    local required_files=(
        "infra/azure/main.bicep"
        "infra/azure/parameters.${ENVIRONMENT}.json"
        "requirements-azure.txt"
        "startup.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✓ Found: $file"
        else
            log_error "✗ Missing required file: $file"
            exit 1
        fi
    done
}

set_azure_context() {
    log_info "Setting Azure context..."
    
    # Set subscription
    az account set --subscription "$SUBSCRIPTION_ID"
    log_success "✓ Set subscription: $SUBSCRIPTION_ID"
    
    # Register required resource providers
    local providers=(
        "Microsoft.Web"
        "Microsoft.DBforPostgreSQL"
        "Microsoft.KeyVault"
        "Microsoft.Storage"
        "Microsoft.Communication"
        "Microsoft.Insights"
        "Microsoft.OperationalInsights"
    )
    
    for provider in "${providers[@]}"; do
        log_info "Registering provider: $provider"
        az provider register --namespace "$provider" --wait
    done
    log_success "✓ Resource providers registered"
}

create_resource_group_if_not_exists() {
    log_info "Checking resource group: $RESOURCE_GROUP_NAME"
    
    if az group exists --name "$RESOURCE_GROUP_NAME" | grep -q "false"; then
        log_info "Creating resource group: $RESOURCE_GROUP_NAME"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_warning "[DRY RUN] Would create resource group: $RESOURCE_GROUP_NAME in $LOCATION"
        else
            az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"
            log_success "✓ Resource group created: $RESOURCE_GROUP_NAME"
        fi
    else
        log_success "✓ Resource group exists: $RESOURCE_GROUP_NAME"
    fi
}

deploy_infrastructure() {
    log_info "Deploying Azure infrastructure..."
    
    local deployment_name="stealth-tinko-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
    local template_file="infra/azure/main.bicep"
    local parameters_file="infra/azure/parameters.${ENVIRONMENT}.json"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "[DRY RUN] Would deploy infrastructure with:"
        log_info "  Template: $template_file"
        log_info "  Parameters: $parameters_file"
        log_info "  Deployment: $deployment_name"
        
        # Run what-if analysis
        log_info "Running what-if analysis..."
        az deployment group what-if \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --template-file "$template_file" \
            --parameters "@$parameters_file"
    else
        # Validate deployment first
        log_info "Validating deployment..."
        az deployment group validate \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --template-file "$template_file" \
            --parameters "@$parameters_file"
        
        log_success "✓ Deployment validation passed"
        
        # Deploy infrastructure
        log_info "Deploying infrastructure..."
        az deployment group create \
            --resource-group "$RESOURCE_GROUP_NAME" \
            --name "$deployment_name" \
            --template-file "$template_file" \
            --parameters "@$parameters_file" \
            --verbose
        
        log_success "✓ Infrastructure deployed successfully"
    fi
}

deploy_application() {
    log_info "Deploying application..."
    
    local web_app_name="stealth-tinko-${ENVIRONMENT}-app"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "[DRY RUN] Would deploy application to: $web_app_name"
        return
    fi
    
    # Create deployment package
    log_info "Creating deployment package..."
    local temp_dir=$(mktemp -d)
    
    # Cleanup function
    cleanup() {
        rm -rf "$temp_dir"
        [[ -f "deployment-package.zip" ]] && rm -f "deployment-package.zip"
    }
    trap cleanup EXIT
    
    # Copy application files
    local files_to_copy=(
        "app"
        "migrations"
        "models"
        "services"
        "schemas"
        "tasks"
        "requirements-azure.txt"
        "startup.py"
        "alembic.ini"
    )
    
    for item in "${files_to_copy[@]}"; do
        if [[ -e "$item" ]]; then
            cp -r "$item" "$temp_dir/"
        fi
    done
    
    # Create zip package
    local zip_path="deployment-package.zip"
    (cd "$temp_dir" && zip -r "../$zip_path" .)
    log_success "✓ Deployment package created: $zip_path"
    
    # Deploy to App Service
    log_info "Uploading to App Service..."
    az webapp deployment source config-zip \
        --resource-group "$RESOURCE_GROUP_NAME" \
        --name "$web_app_name" \
        --src "$zip_path"
    
    log_success "✓ Application deployed successfully"
}

run_post_deployment_tasks() {
    log_info "Running post-deployment tasks..."
    
    local web_app_name="stealth-tinko-${ENVIRONMENT}-app"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "[DRY RUN] Would run post-deployment tasks"
        return
    fi
    
    # Wait for deployment to complete
    log_info "Waiting for application to start..."
    sleep 30
    
    # Test application health
    local app_url="https://${web_app_name}.azurewebsites.net"
    local health_url="${app_url}/health"
    
    if curl -f -s "$health_url" > /dev/null; then
        log_success "✓ Application health check passed"
    else
        log_warning "⚠ Health check failed, but deployment may still be successful"
        log_info "Check application logs for details"
    fi
    
    # Show deployment summary
    log_info "============================================"
    log_info "DEPLOYMENT SUMMARY"
    log_info "============================================"
    log_info "Environment: $ENVIRONMENT"
    log_info "Resource Group: $RESOURCE_GROUP_NAME"
    log_info "Application URL: $app_url"
    log_info "Health Check URL: $health_url"
    log_info "============================================"
}

# Main execution
main() {
    deploy_stealth_tinko
}

# Execute main function
main "$@"