# Azure Static Web Apps Deployment Guide

## Overview

Azure Static Web Apps (SWA) provides a streamlined development experience for modern web applications with:

- **Global CDN Distribution**: Your frontend is automatically distributed across Microsoft's global network
- **Integrated CI/CD**: Automatic deployments from GitHub with zero configuration
- **Serverless API Functions**: Lightweight backend functions for authentication and utilities
- **Custom Authentication**: Built-in authentication providers or custom auth flows
- **Free Tier Available**: Generous free tier with production-ready features

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Web    │    │   Azure App     │    │   PostgreSQL    │
│      Apps       │◄──►│    Service      │◄──►│  Flexible SVR   │
│                 │    │                 │    │                 │
│ Frontend + API  │    │ FastAPI Backend │    │   Database      │
│   Functions     │    │  + Auth System  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

1. **Azure Static Web Apps**: Hosts Next.js frontend + lightweight API functions
2. **Azure App Service**: Main FastAPI backend with authentication and business logic
3. **PostgreSQL Flexible Server**: Database with user data and business records

## Files Created

### Frontend Configuration

- `tinko-console/next.config.ts`: Enhanced for static export compatibility
- `tinko-console/package.json`: Added SWA build scripts (`build:static`, `build:swa`)
- `tinko-console/lib/api-config.ts`: Cross-service communication configuration
- `tinko-console/staticwebapp.config.json`: SWA routing and security headers

### API Functions

- `api/host.json`: Azure Functions runtime configuration
- `api/package.json`: Node.js dependencies for API functions
- `api/health/`: Health check function for monitoring both SWA and backend
- `api/auth/`: JWT token validation function for lightweight auth operations

### Deployment

- `.github/workflows/azure-static-web-apps.yml`: Automated CI/CD workflow
- `deploy-swa.ps1`: PowerShell script for initial Azure resource creation

## Deployment Steps

### 1. Prerequisites

- Azure CLI installed and logged in: `az login`
- GitHub repository with your code
- Active Azure subscription

### 2. Update GitHub Repository URL

Edit `deploy-swa.ps1` line 12:
```powershell
$githubRepo = "https://github.com/YOUR_GITHUB_USERNAME/STEALTH-TINKO"
```

### 3. Deploy Azure Resources

```powershell
# Run the deployment script
.\deploy-swa.ps1
```

This script will:
- Create resource group if needed
- Create Azure Static Web App
- Configure GitHub integration
- Provide deployment token

### 4. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

1. **AZURE_STATIC_WEB_APPS_API_TOKEN**: From deployment script output
2. **JWT_SECRET**: Your JWT secret key (same as backend)

### 5. Push and Deploy

```bash
git add .
git commit -m "Add Azure Static Web Apps configuration"
git push origin main
```

The GitHub Actions workflow will automatically:
- Build the Next.js application for static export
- Install API function dependencies
- Deploy to Azure Static Web Apps

## Configuration Details

### Cross-Service Communication

The `api-config.ts` file configures how the frontend communicates with both services:

```typescript
// Determines which API to use based on function type
const getApiUrl = (endpoint: string): string => {
  if (endpoint.startsWith('/health') || endpoint.startsWith('/auth/validate')) {
    return SWA_API_BASE; // Use SWA functions for lightweight operations
  }
  return API_BASE; // Use main backend for business logic
};
```

### Authentication Flow

1. **Login**: Frontend sends credentials to main backend API
2. **Token Storage**: JWT token stored in localStorage
3. **Validation**: SWA API functions can validate tokens locally
4. **API Calls**: Frontend includes token in Authorization header

### Environment Variables

The SWA deployment uses these environment variables:

- `NEXT_PUBLIC_API_URL`: Main backend URL for API calls
- `NEXT_PUBLIC_APP_NAME`: Application name for branding
- `BACKEND_BASE_URL`: Backend URL for API functions
- `JWT_SECRET`: Secret for token validation (stored in GitHub secrets)

## Benefits of This Architecture

### Performance
- **CDN Distribution**: Frontend served from edge locations globally
- **Static Generation**: Pre-built pages for fastest loading
- **Optimized Assets**: Automatic compression and optimization

### Developer Experience
- **Zero-Config Deployment**: Push to deploy automatically
- **Preview Deployments**: Automatic staging environments for pull requests
- **Integrated Monitoring**: Built-in analytics and logging

### Cost Efficiency
- **Free Tier**: Generous limits for development and small production apps
- **Pay-as-Scale**: Only pay for what you use beyond free tier
- **Reduced Bandwidth Costs**: CDN reduces origin server load

### Security
- **HTTPS Everywhere**: Automatic SSL certificates
- **Header Security**: Security headers configured by default
- **DDoS Protection**: Built-in protection from Azure's network

## Monitoring and Management

### Static Web App URLs

After deployment, your app will be available at:
- **Production**: `https://[swa-name]-[random].azurestaticapps.net`
- **Custom Domain**: Configure in Azure Portal

### Health Monitoring

- **SWA Health**: `https://your-swa-url/api/health`
- **Backend Health**: `https://stealth-tinko-prod-app-1762804410.azurewebsites.net/health`

### Azure Portal Management

Visit: `https://portal.azure.com` → Resource Groups → `stealth-tinko-rg` → `stealth-tinko-swa`

Configure:
- Custom domains
- Environment variables
- Authentication providers
- Function settings
- Analytics and monitoring

## Troubleshooting

### Common Issues

1. **Build Failures**: Check GitHub Actions logs for dependency or build errors
2. **API Function Errors**: Check Azure Functions logs in the portal
3. **Routing Issues**: Verify `staticwebapp.config.json` configuration
4. **CORS Errors**: Ensure proper headers in API functions

### Debug Steps

1. Check GitHub Actions workflow status
2. Review Azure Functions logs
3. Test API endpoints individually
4. Verify environment variables

## Next Steps

1. **Custom Domain**: Configure your own domain in Azure Portal
2. **Authentication Providers**: Add Google, Microsoft, or other OAuth providers
3. **Function Scaling**: Monitor usage and adjust function scaling settings
4. **Performance Optimization**: Use Azure CDN analytics to optimize content delivery

## Cost Optimization

### Free Tier Limits
- 100 GB bandwidth per month
- 0.5 GB storage
- Custom domains included
- Always-on SSL

### Monitoring Usage
- Track bandwidth and storage in Azure Portal
- Set up billing alerts for cost management
- Use Application Insights for detailed analytics

This architecture provides enterprise-grade performance and reliability while maintaining the simplicity of your existing FastAPI backend and the power of modern frontend deployment.