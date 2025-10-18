# 🚀 Tinko Recovery - Deployment & Testing Guide

## 📋 Overview

This guide covers deploying Tinko Recovery to production with full PWA support and cross-platform compatibility.

## ✅ Pre-Deployment Checklist

### Code Quality

- [ ] All TypeScript errors resolved
- [ ] ESLint warnings addressed
- [ ] No console.logs in production code
- [ ] Environment variables configured
- [ ] API endpoints verified

### PWA Requirements

- [ ] manifest.json accessible at /manifest.json
- [ ] All icon sizes generated (72px to 512px)
- [ ] Maskable icons created (192px, 512px)
- [ ] Service worker configured
- [ ] Offline page created
- [ ] Install prompt component added

### Performance

- [ ] Images optimized (WebP/AVIF)
- [ ] Fonts preloaded
- [ ] Code splitting implemented
- [ ] Lazy loading configured
- [ ] Lighthouse score >95

### Accessibility

- [ ] ARIA labels added
- [ ] Keyboard navigation works
- [ ] Focus management implemented
- [ ] Color contrast verified (WCAG AA)
- [ ] Screen reader tested

### Security

- [ ] HTTPS enabled
- [ ] CSP headers configured
- [ ] XSS protection enabled
- [ ] CORS properly configured
- [ ] Auth tokens secure

## 🌐 Deployment Options

### Option 1: Vercel (Recommended)

#### Initial Setup

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link
```

#### Environment Variables

Configure in Vercel Dashboard or CLI:

```bash
# Production
vercel env add AUTH_SECRET production
vercel env add NEXTAUTH_URL production

# Preview (optional)
vercel env add AUTH_SECRET preview
vercel env add NEXTAUTH_URL preview
```

Required Variables:

```
AUTH_SECRET=<generate with: openssl rand -base64 32>
NEXTAUTH_URL=https://www.tinko.in
NEXT_PUBLIC_APP_URL=https://www.tinko.in
```

#### Deploy

```bash
# Deploy to production
vercel --prod

# Deploy to preview
vercel
```

#### Post-Deployment

1. Visit https://www.tinko.in
2. Verify manifest.json loads
3. Test PWA install on mobile
4. Check service worker registration
5. Run Lighthouse audit

### Option 2: Netlify

#### Setup

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Login
netlify login

# Initialize
netlify init
```

#### Configuration (netlify.toml)

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NODE_VERSION = "20"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/sw.js"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
    Service-Worker-Allowed = "/"
```

#### Deploy

```bash
netlify deploy --prod
```

### Option 3: Self-Hosted (Node.js)

#### Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2

# Create app user
sudo useradd -m -s /bin/bash tinko
```

#### Application Setup

```bash
# Clone repository
cd /home/tinko
git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git app
cd app/tinko-console

# Install dependencies
npm ci --production

# Build
npm run build

# Configure environment
cat > .env.local <<EOF
AUTH_SECRET=<generated-secret>
NEXTAUTH_URL=https://www.tinko.in
NODE_ENV=production
EOF

# Start with PM2
pm2 start npm --name "tinko-recovery" -- start
pm2 save
pm2 startup
```

#### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.tinko.in tinko.in;

    ssl_certificate /etc/letsencrypt/live/tinko.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tinko.in/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Service worker
    location = /sw.js {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=0, must-revalidate";
        add_header Service-Worker-Allowed "/";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name www.tinko.in tinko.in;
    return 301 https://$server_name$request_uri;
}
```

## 🧪 Testing Strategy

### Local Testing

#### Development Server

```bash
npm run dev
# Test at http://localhost:3000
```

#### Production Build

```bash
npm run build
npm start
# Test at http://localhost:3000
```

### Cross-Platform Testing

#### Android (Real Device)

1. Enable USB debugging
2. Connect via USB
3. Open Chrome DevTools → chrome://inspect
4. Select device and inspect
5. Test PWA install via Chrome menu

#### iOS (Real Device - macOS Required)

1. Enable Web Inspector (Settings → Safari → Advanced)
2. Connect via USB
3. Open Safari → Develop → [Device]
4. Test "Add to Home Screen"

#### Desktop

```bash
# Windows
- Test in Edge, Chrome, Firefox

# macOS
- Test in Safari, Chrome, Edge

# Linux
- Test in Chrome, Firefox
```

### Automated Testing

#### Lighthouse CI

```bash
# Install
npm install -g @lhci/cli

# Configure (lighthouserc.json)
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.95}],
        "categories:accessibility": ["error", {"minScore": 1.0}],
        "categories:best-practices": ["error", {"minScore": 1.0}],
        "categories:seo": ["error", {"minScore": 1.0}],
        "categories:pwa": ["error", {"minScore": 1.0}]
      }
    }
  }
}

# Run
npm run build
npm start &
lhci autorun
```

#### Playwright (E2E Testing)

```bash
# Install
npm install -D @playwright/test

# Run tests
npx playwright test

# Generate report
npx playwright show-report
```

### Performance Testing

#### Core Web Vitals

```bash
# Install web-vitals
npm install web-vitals

# Add to app
import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

#### Load Testing

```bash
# Install artillery
npm install -g artillery

# Create test config (artillery.yml)
config:
  target: "https://www.tinko.in"
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Homepage"
    flow:
      - get:
          url: "/"

# Run
artillery run artillery.yml
```

## 🔍 Monitoring & Analytics

### Vercel Analytics

```bash
# Install
npm install @vercel/analytics

# Add to app/layout.tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### Sentry Error Tracking

```bash
# Install
npm install @sentry/nextjs

# Configure (sentry.client.config.ts)
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});
```

### Google Analytics 4

```bash
# Add to app/layout.tsx
<Script
  src={`https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX`}
  strategy="afterInteractive"
/>
<Script id="google-analytics" strategy="afterInteractive">
  {`
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  `}
</Script>
```

## 📊 Post-Deployment Validation

### 1. PWA Functionality

```bash
# Check manifest
curl https://www.tinko.in/manifest.json

# Check service worker
curl https://www.tinko.in/sw.js

# Verify icons
curl -I https://www.tinko.in/icons/icon-192x192.png.svg
```

### 2. Security Headers

```bash
curl -I https://www.tinko.in | grep -E "X-Frame-Options|X-Content-Type-Options|Referrer-Policy"
```

### 3. Performance

```bash
# Run Lighthouse
npx lighthouse https://www.tinko.in --view

# Check PageSpeed Insights
https://pagespeed.web.dev/analysis?url=https://www.tinko.in
```

### 4. Mobile Friendliness

```bash
# Google Mobile-Friendly Test
https://search.google.com/test/mobile-friendly?url=https://www.tinko.in
```

### 5. SSL Certificate

```bash
# Check SSL
openssl s_client -connect www.tinko.in:443 -servername www.tinko.in
```

## 🐛 Troubleshooting

### PWA Not Installing

1. Verify manifest.json is accessible
2. Check all required icons exist
3. Ensure HTTPS is enabled
4. Verify service worker registers
5. Check browser console for errors

### Service Worker Issues

```javascript
// Unregister and re-register
navigator.serviceWorker.getRegistrations().then((registrations) => {
  registrations.forEach((registration) => registration.unregister());
});

// Then reload page
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

### Performance Issues

1. Enable compression (gzip/brotli)
2. Optimize images (use WebP/AVIF)
3. Enable caching headers
4. Use CDN for static assets
5. Minimize JavaScript bundles

## 📈 Continuous Deployment

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci
        working-directory: ./tinko-console

      - name: Run tests
        run: npm test
        working-directory: ./tinko-console

      - name: Build
        run: npm run build
        working-directory: ./tinko-console

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID}}
          vercel-project-id: ${{ secrets.PROJECT_ID}}
          vercel-args: "--prod"
          working-directory: ./tinko-console
```

## 🎉 Success Criteria

### Deployment Complete When:

- [ ] App accessible at https://www.tinko.in
- [ ] SSL certificate valid
- [ ] PWA installable on Android/iOS
- [ ] Service worker active
- [ ] Lighthouse scores all >95
- [ ] No console errors
- [ ] Analytics tracking
- [ ] Error monitoring active
- [ ] All environment variables set
- [ ] Backup strategy in place

## 🆘 Support

- **Documentation**: /docs/CROSS-PLATFORM.md
- **Issues**: GitHub Issues
- **Email**: support@tinko.in
- **Status Page**: https://status.tinko.in (future)

---

**Ready to deploy? Follow the checklist above and ship with confidence! 🚢**
