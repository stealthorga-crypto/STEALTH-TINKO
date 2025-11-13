# 🚀 Customer Portal Setup Guide

## Overview
This guide will help you set up and deploy the STEALTH-TINKO Customer Portal with authentication to **tinko.in** (GoDaddy hosting).

## 📋 Prerequisites

- Git installed on your computer
- Node.js 18+ installed
- GoDaddy hosting account with tinko.in
- Code editor (VS Code recommended)

---

## Step 1: Clone the Repository Locally

Open your terminal/command prompt and run:

```bash
# Clone the repository
git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git

# Navigate into the project
cd STEALTH-TINKO

# Create a new branch for customer portal
git checkout -b customer-portal-frontend
```

---

## Step 2: Create Customer Portal Directory

```bash
# Create new directory for customer portal
mkdir customer-portal
cd customer-portal

# Initialize package.json
npm init -y

# Install dependencies
npm install next react react-dom
npm install -D typescript @types/react @types/node tailwindcss postcss autoprefixer

# Initialize Tailwind CSS
npx tailwindcss init -p
```

---

## Step 3: Create Project Structure

Create the following folder structure:

```
customer-portal/
├── app/
│   ├── login/
│   │   └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   ├── recovery/
│   │   └── page.tsx
│   ├── settings/
│   │   └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── Auth/
│   │   ├── LoginForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── Dashboard/
│   │   ├── Stats.tsx
│   │   ├── RecoveryTable.tsx
│   │   └── Charts.tsx
│   └── Layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── auth.ts
│   └── api.ts
├── public/
│   └── logo.png
├── styles/
│   └── globals.css
├── .env.local
├── next.config.js
├── package.json
└── tsconfig.json
```

---

## Step 4: Install Required Files

Run this command to create all necessary files:

```bash
# Create directories
mkdir -p app/login app/dashboard app/recovery app/settings components/Auth components/Dashboard components/Layout lib public styles

# Create empty files
touch app/login/page.tsx app/dashboard/page.tsx app/recovery/page.tsx app/settings/page.tsx
touch app/layout.tsx app/page.tsx
touch components/Auth/LoginForm.tsx components/Auth/ProtectedRoute.tsx
touch components/Dashboard/Stats.tsx components/Dashboard/RecoveryTable.tsx components/Dashboard/Charts.tsx
touch components/Layout/Header.tsx components/Layout/Sidebar.tsx components/Layout/Footer.tsx
touch lib/auth.ts lib/api.ts
touch styles/globals.css
touch .env.local
touch next.config.js
touch tsconfig.json
```

---

## Step 5: Key File Contents

### `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=https://tinko.in
```

### `next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'out',
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
```

### `tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### `tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## Step 6: Build and Test Locally

```bash
# In customer-portal directory
npm run dev

# Open browser to http://localhost:3000
# Test all pages and authentication
```

---

## Step 7: Build for Production

```bash
# Create production build
npm run build

# This creates an 'out' folder with static files
```

---

## Step 8: Deploy to GoDaddy (tinko.in)

### Option A: Manual Upload via File Manager

1. Log in to your GoDaddy account
2. Go to **My Products** → **Web Hosting** → **Manage**
3. Open **File Manager** or **cPanel**
4. Navigate to `public_html` folder
5. Delete existing files (if any)
6. Upload all files from the `out` folder
7. Visit https://tinko.in to see your site

### Option B: Deploy via FTP

1. Get FTP credentials from GoDaddy
2. Use FileZilla or similar FTP client
3. Connect to your hosting:
   - Host: ftp.tinko.in (or provided by GoDaddy)
   - Username: Your FTP username
   - Password: Your FTP password
4. Upload contents of `out` folder to `public_html`

### Option C: Automated Deployment (GitHub Actions)

Create `.github/workflows/deploy.yml` in your repo root:

```yaml
name: Deploy to GoDaddy

on:
  push:
    branches:
      - main
    paths:
      - 'customer-portal/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        working-directory: ./customer-portal
        run: npm install
      
      - name: Build
        working-directory: ./customer-portal
        run: npm run build
      
      - name: Deploy via FTP
        uses: SamKirkland/FTP-Deploy-Action@4.3.3
        with:
          server: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          local-dir: ./customer-portal/out/
          server-dir: /public_html/
```

Add secrets in GitHub: **Settings** → **Secrets** → **Actions**
- `FTP_SERVER`
- `FTP_USERNAME`
- `FTP_PASSWORD`

---

## Step 9: Configure Domain DNS (If Needed)

In GoDaddy DNS settings:
1. Go to **Domains** → **tinko.in** → **DNS**
2. Ensure A record points to your hosting IP
3. Add CNAME if using www subdomain

---

## Step 10: Test Production Site

Visit https://tinko.in and verify:
- ✅ Login page loads
- ✅ Authentication works
- ✅ Dashboard displays correctly
- ✅ All features functional

---

## 🔒 Security Checklist

- [ ] Use HTTPS (SSL certificate from GoDaddy)
- [ ] Rotate exposed Stripe webhook secrets
- [ ] Set up environment variables properly
- [ ] Enable rate limiting on login
- [ ] Implement CSRF protection
- [ ] Use secure session management

---

## 📞 Need Help?

- Email: info@blocksandloops.com
- GitHub Issues: [Create Issue](https://github.com/stealthorga-crypto/STEALTH-TINKO/issues)
- Documentation: See README.md

---

## Next Steps After Deployment

1. **Complete implementation files** - I'll provide complete code for all components
2. **Set up backend API** - Ensure backend is accessible from tinko.in
3. **Configure authentication** - Connect to your auth system
4. **Test thoroughly** - Run through all user flows
5. **Monitor and maintain** - Set up error tracking

---

**Ready to build? Let me know and I'll provide the complete code for all components!**
