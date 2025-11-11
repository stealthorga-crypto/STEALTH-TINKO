# Manual Azure Static Web Apps Setup Guide

Since Azure CLI installation requires admin privileges, here's how to create your Static Web App manually through the Azure Portal.

## Step 1: Create Static Web App in Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Sign in** with your Azure account
3. **Click "Create a resource"** (+ icon in top left)
4. **Search for "Static Web App"** and select it
5. **Click "Create"**

## Step 2: Configure Basic Settings

Fill in these details:

### Basics Tab:
- **Subscription**: Select your subscription
- **Resource Group**: Select `stealth-tinko-rg` (or create new if doesn't exist)
- **Name**: `stealth-tinko-swa`
- **Plan Type**: `Free` (or Standard if you prefer)
- **Azure Functions and staging locations**: `East US 2`

### Deployment Details:
- **Source**: `GitHub`
- **GitHub account**: Connect your GitHub account
- **Organization**: `stealthorga-crypto`
- **Repository**: `STEALTH-TINKO`
- **Branch**: `main`

### Build Details:
- **Build Presets**: `Next.js`
- **App location**: `/tinko-console`
- **Api location**: `/api`
- **Output location**: `out`

## Step 3: Review and Create

1. **Click "Review + Create"**
2. **Verify all settings** are correct
3. **Click "Create"**

Azure will:
- Create the Static Web App resource
- Add a GitHub workflow file to your repository
- Set up automatic deployments

## Step 4: Get Deployment Token

After creation (takes ~5 minutes):

1. **Go to your Static Web App** in the Azure Portal
2. **Click "Manage deployment token"** in the overview
3. **Copy the token** - you'll need this for GitHub secrets

## Step 5: Configure GitHub Secrets

1. **Go to your GitHub repository**: https://github.com/stealthorga-crypto/STEALTH-TINKO
2. **Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**

Add these secrets:

### Secret 1: Azure Deployment Token
- **Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- **Value**: The token from Step 4

### Secret 2: JWT Secret
- **Name**: `JWT_SECRET`
- **Value**: `your-super-secret-jwt-key` (same as your backend)

## Step 6: Trigger Deployment

The GitHub workflow should automatically trigger when you created the SWA, but you can manually trigger it:

1. **Go to GitHub** → **Actions** tab
2. **Find the "Azure Static Web Apps CI/CD" workflow**
3. **Click "Run workflow"** if needed

## Step 7: Monitor Deployment

1. **Watch the GitHub Actions** progress
2. **Check Azure Portal** for deployment status
3. **Your app will be available at**: `https://[generated-name].azurestaticapps.net`

## Expected GitHub Workflow File

Azure should automatically create this file in your repo:
`.github/workflows/azure-static-web-apps-[name].yml`

If it doesn't match our configuration, you can replace it with our existing:
`.github/workflows/azure-static-web-apps.yml`

## Troubleshooting

### If Deployment Fails:

1. **Check GitHub Actions logs** for build errors
2. **Verify paths are correct**:
   - App location: `/tinko-console`
   - API location: `/api`
   - Output location: `out`
3. **Check package.json** has the build scripts:
   - `build:static`
   - `build:swa`

### If Build Fails:

Most common issues:
- **Missing dependencies**: Check `tinko-console/package-lock.json` exists
- **Build command**: Should be `npm run build:swa`
- **Output directory**: Should be `out` (not `build` or `dist`)

### If API Functions Fail:

- **Check `api/package.json`** exists with dependencies
- **Verify function.json** files are correct
- **Check environment variables** are set in GitHub secrets

## Testing Your Deployment

Once deployed, test these endpoints:

1. **Frontend**: `https://your-swa-url/`
2. **Health API**: `https://your-swa-url/api/health`
3. **Auth API**: `https://your-swa-url/api/auth/validate` (POST with token)

## Next Steps After Successful Deployment

1. **Configure custom domain** (if desired) in Azure Portal
2. **Set up monitoring** and alerts
3. **Test the authentication flow** between SWA and your backend
4. **Update your main README.md** with the new URLs

## Benefits You'll Get

- ⚡ **Global CDN**: Your frontend will load faster worldwide
- 🔄 **Auto Deploy**: Push to deploy automatically  
- 💰 **Cost Effective**: Free tier covers most development needs
- 📊 **Built-in Analytics**: Track usage and performance
- 🔒 **Enterprise Security**: HTTPS, security headers, DDoS protection

Your existing backend at `stealth-tinko-prod-app-1762804410.azurewebsites.net` continues to work unchanged - this just adds a powerful frontend delivery layer!