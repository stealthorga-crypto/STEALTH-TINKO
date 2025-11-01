# 🧪 Testing Checklist - Tinko Recovery PWA

## Quick Testing Guide

Use this checklist to verify all cross-platform features work correctly.

---

## ✅ Pre-Deployment Tests (Development)

### 1. Build & Start

```bash
cd tinko-console
npm run build
npm start
```

Visit: http://localhost:3000

### 2. Basic Functionality

- [ ] Homepage loads without errors
- [ ] Navigation works (all menu items)
- [ ] Sign in page accessible
- [ ] Authentication works (test@example.com / any password)
- [ ] Dashboard loads after login
- [ ] All console pages accessible (Dashboard, Rules, Settings, etc.)
- [ ] Logout works

### 3. Responsive Design

Open DevTools (F12) → Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)

- [ ] **Mobile (375px)**: Content fits, no horizontal scroll, buttons tappable
- [ ] **Tablet (768px)**: Layout adapts, sidebar behavior correct
- [ ] **Desktop (1920px)**: Full layout visible, spacing correct
- [ ] **4K (3840px)**: No pixelation, content not stretched

### 4. PWA Features

Open Chrome DevTools → Application tab

- [ ] Manifest.json loads (check Application → Manifest)
- [ ] All icons present (192px, 512px, maskable)
- [ ] Service worker registered (check Service Workers)
- [ ] Cache storage created (check Cache Storage)

---

## 📱 Platform-Specific Tests

### Android Testing

#### Requirements

- Android 11+ device
- Chrome browser
- Same WiFi as dev machine

#### Steps

1. **Access App**

   ```
   http://[YOUR_IP]:3000
   Example: http://192.168.1.100:3000
   ```

2. **Install PWA**

   - [ ] Open in Chrome
   - [ ] Wait 30 seconds for install prompt
   - [ ] OR tap Chrome menu → "Install app"
   - [ ] App icon appears on home screen

3. **Test Installed App**

   - [ ] Open from home screen (standalone mode)
   - [ ] No browser UI visible
   - [ ] Theme color applied to status bar
   - [ ] Long-press icon shows shortcuts (Dashboard, Rules, Settings)

4. **Touch Interactions**

   - [ ] All buttons respond to touch
   - [ ] No accidental double-taps
   - [ ] Swipe gestures work (where applicable)
   - [ ] Keyboard appears for input fields

5. **Offline Mode**
   - [ ] Turn on Airplane mode
   - [ ] App still loads
   - [ ] Previously viewed pages accessible
   - [ ] Offline page shows when navigating to new pages
   - [ ] Network status banner shows "No internet"
   - [ ] Turn off Airplane mode
   - [ ] "Back online" banner appears

#### Android Debug Mode

```bash
# Enable USB debugging on device
# Connect via USB
chrome://inspect

# Select device → Inspect
# Run Lighthouse audit
```

---

### iOS Testing

#### Requirements

- iPhone/iPad with iOS 15+
- Safari browser
- macOS with Xcode (for debugging)

#### Steps

1. **Access App**

   ```
   http://[YOUR_IP]:3000
   ```

2. **Install PWA**

   - [ ] Open in Safari
   - [ ] Tap Share button (square with arrow)
   - [ ] Scroll → "Add to Home Screen"
   - [ ] Edit name if desired
   - [ ] Tap "Add"
   - [ ] Icon appears on home screen

3. **Test Installed App**

   - [ ] Launch from home screen
   - [ ] Full-screen mode (no Safari UI)
   - [ ] Status bar color matches theme
   - [ ] Safe area insets respected (notch areas)

4. **Touch Interactions**

   - [ ] Tap targets minimum 48x48px
   - [ ] No zoom on input focus (font-size ≥16px)
   - [ ] Smooth scrolling
   - [ ] Swipe back gesture works

5. **Limitations (iOS)**
   - [ ] Service worker limited to 50MB cache
   - [ ] Push notifications not available
   - [ ] Background sync not available
   - ℹ️ These are Safari/iOS restrictions

#### iOS Debug Mode (macOS Required)

```bash
# On iPhone: Settings → Safari → Advanced → Web Inspector (ON)
# Connect iPhone via USB
# On Mac: Safari → Develop → [iPhone Name] → [Page]
```

---

### Windows Testing

#### Requirements

- Windows 10 or 11
- Chrome or Edge browser

#### Steps

1. **Access App**

   ```
   http://localhost:3000
   ```

2. **Install PWA**

   - [ ] Look for install icon in address bar (⊕ or monitor icon)
   - [ ] Click install
   - [ ] OR use Chrome menu → "Install Tinko Recovery"
   - [ ] App opens in separate window
   - [ ] App appears in Start Menu

3. **Test Installed App**

   - [ ] Launch from Start Menu
   - [ ] No browser UI (standalone window)
   - [ ] Window resizable
   - [ ] Taskbar icon present
   - [ ] Can pin to taskbar

4. **Keyboard Navigation**

   - [ ] Tab through all interactive elements
   - [ ] Enter activates buttons/links
   - [ ] Escape closes modals
   - [ ] Arrow keys work in forms

5. **Offline Mode**
   - [ ] Open DevTools (F12)
   - [ ] Network tab → Throttling → Offline
   - [ ] App continues to work
   - [ ] Offline page shows for new routes

---

### macOS Testing

#### Requirements

- macOS Monterey or later
- Chrome, Edge, or Safari

#### Steps (Chrome/Edge)

1. **Install PWA**

   - [ ] Click install icon in address bar
   - [ ] App opens in separate window
   - [ ] App appears in Applications folder
   - [ ] Dock icon present

2. **Test Features**
   - [ ] Command+Tab shows app
   - [ ] Window controls work (traffic lights)
   - [ ] Full-screen mode available
   - [ ] Touch Bar support (if available)

#### Steps (Safari)

- [ ] Safari has limited PWA support
- [ ] Use Chrome/Edge for full PWA experience
- [ ] Web app works fine in Safari browser

---

### Linux Testing

#### Requirements

- Ubuntu 22.04 or similar
- Chrome or Firefox

#### Steps

1. **Install PWA (Chrome)**

   - [ ] Click install icon in omnibox
   - [ ] OR Chrome menu → "Install Tinko Recovery"
   - [ ] .desktop file created
   - [ ] App appears in application launcher

2. **Test Features**
   - [ ] Launch from app menu
   - [ ] Standalone window
   - [ ] Integrates with desktop environment
   - [ ] Respects system theme (future enhancement)

---

## 🔍 Advanced Testing

### Lighthouse Audit

```bash
npm run build
npm start
npx lighthouse http://localhost:3000 --view
```

**Expected Scores:**

- Performance: >95
- Accessibility: 100
- Best Practices: 100
- SEO: 100
- PWA: All checks ✓

### Network Conditions

Test with different network speeds:

1. **Chrome DevTools** → Network tab → Throttling
   - [ ] Fast 3G: Loads reasonably
   - [ ] Slow 3G: Essential content visible
   - [ ] Offline: Cached pages accessible

### Accessibility Testing

#### Keyboard Only

- [ ] Navigate entire app with Tab/Shift+Tab
- [ ] All interactive elements reachable
- [ ] Focus indicators visible
- [ ] No keyboard traps

#### Screen Reader

- [ ] Use NVDA (Windows) or VoiceOver (Mac)
- [ ] All images have alt text
- [ ] Headings properly structured (h1 → h6)
- [ ] Form labels associated with inputs
- [ ] ARIA labels present where needed

#### Color Contrast

- [ ] Use axe DevTools extension
- [ ] No contrast failures
- [ ] Text readable on all backgrounds

### Performance Testing

#### First Load

```bash
# Clear cache
# Load homepage
# Check metrics:
- FCP: <1.8s
- LCP: <2.5s
- TTI: <3.8s
- TBT: <200ms
- CLS: <0.1
```

#### Bundle Size

```bash
npm run build

# Check output:
# Route            Size       First Load JS
# /                ~150 KB    ~200 KB
# /dashboard       ~160 KB    ~210 KB
```

---

## 🐛 Common Issues & Solutions

### Issue: PWA Install Not Showing

**Solution:**

1. Verify HTTPS (localhost exempt)
2. Check manifest.json is accessible
3. Ensure all required icons exist
4. Clear browser cache
5. Wait 30 seconds for install prompt

### Issue: Service Worker Not Updating

**Solution:**

```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then((regs) => {
  regs.forEach((reg) => reg.unregister());
});
// Reload page
```

### Issue: Offline Mode Not Working

**Solution:**

1. Check service worker registered (DevTools → Application)
2. Verify caching strategy in next.config.ts
3. Build production bundle (dev mode disables SW)
4. Check Network tab for cached responses

### Issue: Icons Not Displaying

**Solution:**

1. Run icon generation script: `node scripts/generate-icons.js`
2. Verify files in `/public/icons/`
3. Check manifest.json paths
4. Clear browser cache

---

## ✅ Production Deployment Tests

After deploying to https://www.tinko.in:

### 1. SSL/HTTPS

```bash
curl -I https://www.tinko.in | grep -i "HTTP/2"
# Should show: HTTP/2 200
```

### 2. Manifest

```bash
curl https://www.tinko.in/manifest.json
# Should return JSON manifest
```

### 3. Service Worker

```bash
curl -I https://www.tinko.in/sw.js
# Should return 200 OK
```

### 4. SEO

- [ ] Google Search Console submitted
- [ ] Sitemap.xml accessible
- [ ] Robots.txt configured
- [ ] OpenGraph preview works (share on social media)

### 5. Real Device Testing

- [ ] Test on actual Android device
- [ ] Test on actual iPhone
- [ ] Test on Windows PC
- [ ] Test on Mac
- [ ] Install and use for 1 week

---

## 📊 Success Criteria

✅ **PASS** if all checkboxes above are completed without major issues.

### Must Have

- Installs on Android & iOS
- Works offline (cached pages)
- Lighthouse scores >90
- Responsive 320px to 4K
- No critical accessibility violations

### Nice to Have

- App shortcuts work
- Network status detection
- Install prompt dismissal logic
- Platform-specific optimizations

---

## 📞 Need Help?

- Check documentation: /docs/CROSS-PLATFORM.md
- Review deployment guide: /docs/DEPLOYMENT.md
- Open issue on GitHub
- Email: support@tinko.in

---

**Happy Testing! 🚀**
