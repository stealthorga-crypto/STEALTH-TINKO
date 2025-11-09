// =======================================
// STEALTH-TINKO Azure Infrastructure
// FastAPI Payment Recovery Platform
// =======================================

// Parameters
@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Application name prefix')
param applicationName string = 'stealth-tinko'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Administrator email for notifications and SSL certificates')
param adminEmail string

@description('GitHub repository for CI/CD deployment')
param gitHubRepo string = 'https://github.com/your-org/stealth-tinko'

@description('PostgreSQL administrator login')
@secure()
param postgresAdminUser string

@description('PostgreSQL administrator password')
@secure()
param postgresAdminPassword string

@description('Email service domain for Communication Services')
param emailDomain string

// Variables
var resourceNamePrefix = '${applicationName}-${environment}'
var appServicePlanName = '${resourceNamePrefix}-plan'
var webAppName = '${resourceNamePrefix}-app'
var keyVaultName = '${resourceNamePrefix}-kv-${uniqueString(resourceGroup().id)}'
var postgresServerName = '${resourceNamePrefix}-db-${uniqueString(resourceGroup().id)}'
var communicationServiceName = '${resourceNamePrefix}-comm-${uniqueString(resourceGroup().id)}'
var applicationInsightsName = '${resourceNamePrefix}-insights'
var logAnalyticsWorkspaceName = '${resourceNamePrefix}-logs'
var storageAccountName = '${toLower(replace(resourceNamePrefix, '-', ''))}st${uniqueString(resourceGroup().id)}'

// SKUs based on environment
var skuConfig = {
  dev: {
    appServicePlan: 'B1'
    postgres: 'Standard_B1ms'
    storage: 'Standard_LRS'
  }
  staging: {
    appServicePlan: 'S1'
    postgres: 'Standard_B2s'
    storage: 'Standard_GRS'
  }
  prod: {
    appServicePlan: 'P1V3'
    postgres: 'Standard_D2s_v3'
    storage: 'Standard_GRS'
  }
}

// =======================================
// Log Analytics Workspace
// =======================================
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environment == 'prod' ? 90 : 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// =======================================
// Application Insights
// =======================================
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// =======================================
// Storage Account
// =======================================
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: skuConfig[environment].storage
  }
  kind: 'StorageV2'
  properties: {
    defaultToOAuthAuthentication: false
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

// =======================================
// Key Vault
// =======================================
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    enablePurgeProtection: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// =======================================
// PostgreSQL Flexible Server
// =======================================
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: postgresServerName
  location: location
  sku: {
    name: skuConfig[environment].postgres
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    version: '15'
    storage: {
      storageSizeGB: environment == 'prod' ? 128 : 32
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: environment == 'prod' ? 35 : 7
      geoRedundantBackup: environment == 'prod' ? 'Enabled' : 'Disabled'
    }
    highAvailability: {
      mode: environment == 'prod' ? 'ZoneRedundant' : 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Enabled'
      dayOfWeek: 0
      startHour: 2
      startMinute: 0
    }
  }
}

// PostgreSQL Database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  parent: postgresServer
  name: 'stealth_tinko_db'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// PostgreSQL Firewall Rule for Azure Services
resource postgresFirewallAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-12-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// =======================================
// Communication Services
// =======================================
resource communicationService 'Microsoft.Communication/communicationServices@2023-06-01-preview' = {
  name: communicationServiceName
  location: 'global'
  properties: {
    dataLocation: 'United States'
  }
}

// Email Communication Service
resource emailCommunicationService 'Microsoft.Communication/emailServices@2023-06-01-preview' = {
  name: '${communicationServiceName}-email'
  location: 'global'
  properties: {
    dataLocation: 'United States'
  }
}

// Email Domain
resource emailServiceDomain 'Microsoft.Communication/emailServices/domains@2023-06-01-preview' = {
  parent: emailCommunicationService
  name: emailDomain
  properties: {
    domainManagement: 'CustomerManaged'
  }
}

// =======================================
// App Service Plan
// =======================================
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: skuConfig[environment].appServicePlan
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// =======================================
// Web App (FastAPI Application)
// =======================================
resource webApp 'Microsoft.Web/sites@2024-11-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: environment != 'dev'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      appSettings: [
        {
          name: 'ENVIRONMENT'
          value: environment
        }
        {
          name: 'DATABASE_URL'
          value: 'postgresql://${postgresAdminUser}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${postgresDatabase.name}?sslmode=require'
        }
        {
          name: 'AZURE_KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=communication-service-connection-string)'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'GOOGLE_CLIENT_ID'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=google-client-id)'
        }
        {
          name: 'GOOGLE_CLIENT_SECRET'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=google-client-secret)'
        }
        {
          name: 'JWT_SECRET_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=jwt-secret-key)'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'PRE_BUILD_COMMAND'
          value: 'echo "Installing dependencies..."'
        }
        {
          name: 'POST_BUILD_COMMAND'
          value: 'echo "Running post-build tasks..."'
        }
        {
          name: 'STARTUP_COMMAND'
          value: 'python -m gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
      ]
      connectionStrings: [
        {
          name: 'DefaultConnection'
          connectionString: 'postgresql://${postgresAdminUser}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${postgresDatabase.name}?sslmode=require'
          type: 'PostgreSQL'
        }
      ]
    }
  }
}

// =======================================
// RBAC Assignments
// =======================================

// Key Vault Secrets User role for Web App
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, webApp.id, 'Key Vault Secrets User')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Blob Data Contributor role for Web App
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, webApp.id, 'Storage Blob Data Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// =======================================
// Diagnostic Settings
// =======================================
resource webAppDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  scope: webApp
  name: 'default'
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// =======================================
// Outputs
// =======================================
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output webAppName string = webApp.name
output resourceGroupName string = resourceGroup().name
output keyVaultName string = keyVault.name
output postgresServerName string = postgresServer.name
output communicationServiceName string = communicationService.name
output applicationInsightsName string = applicationInsights.name
output storageAccountName string = storageAccount.name

// Connection strings and secrets (for deployment scripts)
output postgresConnectionString string = 'postgresql://${postgresAdminUser}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${postgresDatabase.name}?sslmode=require'
output communicationServiceConnectionString string = communicationService.listKeys().primaryConnectionString
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'