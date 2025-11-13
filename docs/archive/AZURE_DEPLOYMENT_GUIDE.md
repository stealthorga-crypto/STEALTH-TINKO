# STEALTH-TINKO Azure Deployment Guide

This guide provides complete instructions for deploying the STEALTH-TINKO payment recovery platform to Microsoft Azure as a SaaS solution.

## 🏗️ Architecture Overview

The Azure deployment includes:

- **Azure App Service**: Hosts the FastAPI application
- **PostgreSQL Flexible Server**: Database for multi-tenant data
- **Azure Key Vault**: Secure storage for secrets and credentials
- **Azure Communication Services**: Email delivery for OTP and notifications
- **Application Insights**: Monitoring and analytics
- **Azure Storage**: File storage and backups
- **GitHub Actions**: CI/CD pipeline for automated deployments

## 📁 Infrastructure Structure

```
infra/
├── azure/
│   ├── main.bicep                 # Main infrastructure template
│   ├── parameters.dev.json        # Development environment parameters
│   ├── parameters.staging.json    # Staging environment parameters
│   └── parameters.prod.json       # Production environment parameters
├── deploy.ps1                     # PowerShell deployment script
└── deploy.sh                      # Bash deployment script

.github/
└── workflows/
    └── azure-deploy.yml           # CI/CD pipeline

# Environment configurations
.env.dev                           # Development settings
.env.staging                       # Staging settings
.env.prod                          # Production settings

# Azure-specific files
requirements-azure.txt             # Azure dependencies
startup.py                         # Azure startup script
app/azure_config.py               # Azure services integration
```

## 🚀 Quick Start Deployment

### Prerequisites

1. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Subscription** - Active Azure subscription with contributor access
3. **Domain** - For custom domain and email services (optional)
4. **GitHub Repository** - For CI/CD automation

### Manual Deployment

#### 1. Login to Azure
```bash
az login
az account set --subscription "your-subscription-id"
```

#### 2. Deploy Infrastructure (PowerShell)
```powershell
.\infra\deploy.ps1 -Environment dev -SubscriptionId "your-subscription-id"
```

#### 3. Deploy Infrastructure (Bash)
```bash
chmod +x ./infra/deploy.sh
./infra/deploy.sh -e dev -s "your-subscription-id"
```

### Automated CI/CD Deployment

#### 1. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
AZURE_CREDENTIALS           # Service principal JSON
AZURE_SUBSCRIPTION_ID       # Your Azure subscription ID
JWT_SECRET_KEY              # JWT signing key
GOOGLE_CLIENT_ID            # Google OAuth client ID
GOOGLE_CLIENT_SECRET        # Google OAuth client secret
```

#### 2. Service Principal Setup

Create a service principal for GitHub Actions:

```bash
az ad sp create-for-rbac \
  --name "stealth-tinko-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth
```

Copy the output JSON to `AZURE_CREDENTIALS` secret.

#### 3. Automatic Deployment

Push to branches for automatic deployment:
- `main` → Production environment
- `staging` → Staging environment  
- `develop` → Development environment

## 🔧 Configuration

### Environment Parameters

Update the parameter files in `infra/azure/` with your specific values:

```json
{
  "parameters": {
    "adminEmail": {
      "value": "your-email@domain.com"
    },
    "emailDomain": {
      "value": "yourdomain.com"
    },
    "postgresAdminUser": {
      "value": "your-admin-user"
    },
    "postgresAdminPassword": {
      "value": "your-secure-password"
    }
  }
}
```

### Azure Key Vault Secrets

After deployment, configure these secrets in Azure Key Vault:

| Secret Name | Description |
|------------|-------------|
| `jwt-secret-key` | JWT signing key |
| `google-client-id` | Google OAuth client ID |
| `google-client-secret` | Google OAuth client secret |
| `stripe-secret-key` | Stripe API secret key |
| `razorpay-key-secret` | Razorpay API secret |

### Database Migration

Database migrations run automatically during deployment. For manual execution:

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:pass@server:5432/db"
export ENVIRONMENT="dev"

# Run migrations
alembic upgrade head
```

## 💰 Cost Estimation

### Development Environment (~$50-100/month)
- App Service Plan (B1): ~$15/month
- PostgreSQL (Standard_B1ms): ~$25/month
- Storage Account: ~$5/month
- Key Vault: ~$3/month
- Communication Services: Pay-per-use
- Application Insights: Free tier

### Production Environment (~$200-500/month)
- App Service Plan (P1V3): ~$80/month
- PostgreSQL (Standard_D2s_v3): ~$150/month
- Storage Account (GRS): ~$15/month
- Key Vault: ~$10/month
- Communication Services: Pay-per-use
- Application Insights: ~$20/month

## 🔐 Security Features

### Infrastructure Security
- ✅ HTTPS enforced on all endpoints
- ✅ TLS 1.2 minimum encryption
- ✅ Network security groups
- ✅ Private endpoints for database
- ✅ Managed identities for service-to-service auth
- ✅ Key Vault for secrets management

### Application Security
- ✅ JWT token authentication
- ✅ Rate limiting and IP blocking
- ✅ Input validation and sanitization
- ✅ CORS policy enforcement
- ✅ SQL injection prevention
- ✅ OWASP security headers

## 📊 Monitoring & Observability

### Application Insights
- Real-time performance metrics
- Custom telemetry and events
- Distributed tracing
- Dependency tracking
- Error tracking and alerting

### Log Analytics
- Centralized logging
- Custom queries (KQL)
- Dashboard creation
- Automated alerting

### Health Checks
- Application health endpoint: `/health`
- Database connectivity checks
- External service availability
- Performance metrics

## 🚨 Troubleshooting

### Common Issues

#### 1. Deployment Fails
```bash
# Check deployment status
az deployment group show \
  --resource-group stealth-tinko-dev-rg \
  --name deployment-name
```

#### 2. Application Won't Start
```bash
# Check application logs
az webapp log tail \
  --resource-group stealth-tinko-dev-rg \
  --name stealth-tinko-dev-app
```

#### 3. Database Connection Issues
```bash
# Test database connectivity
az postgres flexible-server connect \
  --name stealth-tinko-dev-db \
  --admin-user stealthadmin
```

#### 4. Key Vault Access Issues
```bash
# Check Key Vault access policies
az keyvault show \
  --name stealth-tinko-dev-kv \
  --query "properties.accessPolicies"
```

### Debugging Commands

```bash
# View resource group resources
az resource list --resource-group stealth-tinko-dev-rg --output table

# Check App Service configuration
az webapp config show --resource-group stealth-tinko-dev-rg --name stealth-tinko-dev-app

# View PostgreSQL server details
az postgres flexible-server show --resource-group stealth-tinko-dev-rg --name stealth-tinko-dev-db

# Test application endpoints
curl https://stealth-tinko-dev-app.azurewebsites.net/health
curl https://stealth-tinko-dev-app.azurewebsites.net/docs
```

## 🔄 Maintenance

### Regular Tasks
- [ ] Monitor application performance
- [ ] Review security alerts
- [ ] Update dependencies
- [ ] Database backups verification
- [ ] Cost optimization review

### Monthly Tasks
- [ ] Security patch updates
- [ ] Performance optimization
- [ ] Capacity planning review
- [ ] Backup testing
- [ ] Documentation updates

## 📞 Support

For deployment issues or questions:

1. Check the [Azure documentation](https://docs.microsoft.com/en-us/azure/)
2. Review Application Insights for errors
3. Check GitHub Actions logs for CI/CD issues
4. Review Azure Activity Log for infrastructure issues

## 🎯 Next Steps

After successful deployment:

1. **Custom Domain**: Configure custom domain and SSL certificate
2. **Email Domain**: Set up custom email domain in Communication Services
3. **Monitoring**: Configure alerts and dashboards
4. **Backup Strategy**: Implement comprehensive backup procedures
5. **Disaster Recovery**: Set up multi-region deployment
6. **Performance Optimization**: Fine-tune application settings
7. **Security Hardening**: Implement additional security measures

---

🎉 **Congratulations!** Your STEALTH-TINKO application is now running on Azure as a scalable SaaS platform!