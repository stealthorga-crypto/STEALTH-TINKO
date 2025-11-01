# 🌍 Tinko Recovery - Cross-Platform & PWA Guide

## Overview

Tinko Recovery is a fully responsive, installable Progressive Web App (PWA) that works seamlessly across all devices, operating systems, and hardware architectures.

## ✅ Supported Platforms

### Desktop

- **Windows 10/11** (x64, ARM64)
  - Chrome, Edge, Firefox, Opera
- **macOS Monterey+** (Intel, Apple Silicon M1/M2/M3)
  - Safari, Chrome, Edge, Firefox
- **Linux** (x86, x64, ARM)
  - Ubuntu 20.04+, Fedora, Debian
  - Chrome, Firefox, Edge

### Mobile

- **Android 11+** (ARM, ARM64, x86)
  - Chrome, Samsung Internet, Edge, Firefox
  - PWA Installation via Chrome
- **iOS 15+ / iPadOS 15+** (ARM64)
  - Safari (primary), Chrome, Edge
  - Add to Home Screen via Safari

### Responsive Breakpoints

```
xs:  320px - 639px  (Mobile portrait)
sm:  640px - 767px  (Mobile landscape / Small tablets)
md:  768px - 1023px (Tablets)
lg:  1024px - 1279px (Laptops)
xl:  1280px - 1535px (Desktops)
2xl: 1536px+         (Large screens / 4K)
```

## 🚀 Installation

### Android (Chrome)

1. Open https://www.tinko.in in Chrome
2. Tap the three dots menu → "Install app"
3. Or use the in-app install prompt
4. App appears on home screen and app drawer

### iOS / iPadOS (Safari)

1. Open https://www.tinko.in in Safari
2. Tap the Share button (square with arrow)
3. Scroll down → "Add to Home Screen"
4. Tap "Add" in the top right
5. App appears on home screen

### Desktop (Chrome / Edge)

1. Visit https://www.tinko.in
2. Click the install icon in the address bar
3. Or use the in-app install prompt
4. App opens in standalone window

## 🎨 Design Specifications

### Typography

- **Font Family**: Inter (Google Fonts)
- **Fluid Scaling**: Uses CSS clamp() for responsive text
- **Minimum Font Size**: 16px (prevents iOS zoom on input focus)

### Touch Targets

- **Minimum Size**: 48x48px (WCAG AAA compliance)
- **Spacing**: Minimum 8px between tap targets
- **Feedback**: Visual feedback on tap/click

### Color Contrast

- **WCAG AA Compliance**: All text meets 4.5:1 contrast ratio
- **Primary**: #2563eb (blue-600)
- **Background**: #ffffff (white)
- **Text**: #0f172a (slate-900)

### Safe Areas

- **iOS Notch Support**: Automatically handled via `env(safe-area-inset-*)`
- **Android Cutouts**: Respects display cutouts
- **Padding**: Applied via `.safe-areas` class

## 🔧 Technical Features

### PWA Capabilities

- ✅ Installable on all platforms
- ✅ Works offline with service worker
- ✅ App shortcuts (Dashboard, Rules, Settings)
- ✅ Splash screens (auto-generated)
- ✅ Theme color customization
- ✅ Full-screen mode option
- ✅ Network status detection
- ✅ Background sync (future)

### Performance Optimizations

- **Next.js Image**: Automatic image optimization
- **Caching Strategy**:
  - Static assets: CacheFirst (1 year)
  - API calls: NetworkFirst (5 min cache)
  - Fonts: CacheFirst (1 year)
- **Code Splitting**: Automatic via Next.js
- **Lazy Loading**: Components load on demand

### Accessibility (A11Y)

- ✅ Keyboard navigation support
- ✅ Screen reader compatible (ARIA labels)
- ✅ Focus management
- ✅ Skip links for navigation
- ✅ Reduced motion support
- ✅ High contrast mode support

## 📊 Performance Targets

### Lighthouse Scores (Target: >95)

- **Performance**: >95
- **Accessibility**: 100
- **Best Practices**: 100
- **SEO**: 100
- **PWA**: All checks passing

### Core Web Vitals

- **LCP (Largest Contentful Paint)**: <1.5s
- **FID (First Input Delay)**: <100ms
- **CLS (Cumulative Layout Shift)**: <0.1

## 🛠️ Development

### Testing Locally

```bash
# Start dev server
npm run dev

# Access on mobile device (same network)
http://192.168.x.x:3000

# Test PWA features (requires HTTPS or localhost)
# Service worker only runs in production build:
npm run build
npm start
```

### Testing on Different Devices

#### Android Testing

```bash
# Via Chrome DevTools
1. Open chrome://inspect
2. Enable USB debugging on Android
3. Connect device via USB
4. Inspect and test
```

#### iOS Testing

```bash
# Via Safari Developer Tools (macOS only)
1. Enable "Web Inspector" on iOS (Settings → Safari → Advanced)
2. Connect iPhone/iPad via USB
3. Open Safari → Develop → [Device Name]
4. Inspect and test
```

#### Cross-Browser Testing

- **BrowserStack**: https://www.browserstack.com
- **Sauce Labs**: https://saucelabs.com
- **LambdaTest**: https://www.lambdatest.com

### Debugging PWA

#### View Manifest

```
https://www.tinko.in/manifest.json
```

#### Check Service Worker

```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then((registrations) => {
  console.log(registrations);
});
```

#### Clear Service Worker Cache

```javascript
// In browser console
caches.keys().then((keys) => {
  keys.forEach((key) => caches.delete(key));
});
```

## 📱 Platform-Specific Notes

### Android

- **Install Prompt**: Automatic after 30 seconds of engagement
- **Update Mechanism**: Automatic when new version detected
- **Icons**: Uses regular and maskable icons
- **Shortcuts**: Accessible via long-press on app icon

### iOS

- **Install Method**: Manual via Safari Share sheet
- **Limitations**:
  - No install prompt (browser restriction)
  - Service worker has limited cache (50MB)
  - Push notifications not supported
- **Testing**: Must use real device (Simulator doesn't support PWA)

### Windows

- **Edge**: Full PWA support with widgets
- **Chrome**: Standard install experience
- **Start Menu**: App appears in Start Menu after install

### macOS

- **Safari**: Limited PWA support (basic only)
- **Chrome**: Full install with dock icon
- **Menu Bar**: App can be added to menu bar

### Linux

- **Chrome/Edge**: Full PWA support
- **Firefox**: Basic support (improving)
- **Desktop Integration**: .desktop file created

## 🔐 Security

### HTTPS Required

- PWA features require HTTPS in production
- Service workers only work over HTTPS
- Localhost exempt for development

### Content Security Policy

```typescript
// Configured in next.config.ts
contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;";
```

### Permissions

- **Location**: Not requested
- **Camera**: Not requested
- **Microphone**: Not requested
- **Notifications**: Future feature (opt-in)

## 🚢 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Environment variables
NEXTAUTH_URL=https://www.tinko.in
AUTH_SECRET=<generated-secret>
```

### Manual Deployment

```bash
# Build production bundle
npm run build

# Serve with any static host
# Ensure HTTPS is enabled
```

### Post-Deployment Checklist

- [ ] Verify manifest.json accessible
- [ ] Test service worker registration
- [ ] Confirm icons load correctly
- [ ] Test install prompt on Android
- [ ] Verify offline functionality
- [ ] Run Lighthouse audit
- [ ] Test on real devices (iOS, Android, Desktop)

## 📈 Analytics & Monitoring

### Recommended Tools

- **Google Analytics**: User behavior
- **Sentry**: Error tracking
- **Vercel Analytics**: Performance monitoring
- **Hotjar**: User interaction heatmaps

### PWA-Specific Metrics

```javascript
// Track installations
window.addEventListener("appinstalled", (evt) => {
  console.log("App installed");
  // Send to analytics
});

// Track offline usage
window.addEventListener("online", () => {
  console.log("Back online");
});

window.addEventListener("offline", () => {
  console.log("Gone offline");
});
```

## 🐛 Troubleshooting

### PWA Not Installing

1. Verify HTTPS is enabled
2. Check manifest.json is valid (use Chrome DevTools)
3. Ensure all icon sizes present
4. Clear browser cache and retry

### Service Worker Not Updating

```javascript
// Force update
navigator.serviceWorker.getRegistrations().then((registrations) => {
  registrations.forEach((registration) => registration.update());
});
```

### Icons Not Showing

1. Verify icon paths in manifest.json
2. Check icon files exist in /public/icons
3. Clear browser cache
4. Regenerate icons with correct sizes

### Offline Mode Not Working

1. Check service worker registered
2. Verify caching strategy in next.config.ts
3. Test with Chrome DevTools offline mode
4. Check Network tab for cached responses

## 📚 Resources

### Documentation

- [Next.js PWA](https://ducanh-next-pwa.vercel.app/)
- [Web.dev PWA Guide](https://web.dev/progressive-web-apps/)
- [MDN Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

### Tools

- [Manifest Generator](https://www.simicart.com/manifest-generator.html/)
- [PWA Builder](https://www.pwabuilder.com/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

### Testing

- [Chrome DevTools PWA](https://developer.chrome.com/docs/devtools/progressive-web-apps/)
- [Responsive Design Mode](https://developer.mozilla.org/en-US/docs/Tools/Responsive_Design_Mode)

## 🤝 Contributing

Found a bug or have a suggestion for cross-platform improvements? Please open an issue or submit a pull request!

## 📄 License

Proprietary - Tinko Recovery Platform

---

**Built with ❤️ for all devices, everywhere.**
