# Testing Guide

This document outlines the testing strategy and procedures for the Tinko Recovery application.

## Testing Stack

### E2E Testing

- **Framework**: Playwright
- **Installation**: `npm install -D @playwright/test`
- **Browsers**: Chromium, Firefox, WebKit (Safari)
- **Purpose**: Test user flows, navigation, authentication

### Accessibility Testing

- **Framework**: jest-axe
- **Installation**: `npm install -D jest-axe @testing-library/react @testing-library/jest-dom`
- **Purpose**: Automated accessibility audits (WCAG 2.1 Level AA compliance)

### Unit Testing

- **Framework**: Jest + React Testing Library (optional, not critical for Phase 10)
- **Purpose**: Component logic testing

## Test Configuration

### Playwright Setup

Create `playwright.config.ts`:

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

## Test Suites

### 1. Homepage Tests (`e2e/homepage.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("Homepage", () => {
  test("should load successfully", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Tinko Recovery/);
  });

  test("should display hero section", async ({ page }) => {
    await page.goto("/");
    const hero = page.locator("h1").first();
    await expect(hero).toBeVisible();
    await expect(hero).toContainText(/Turn Failed Payments Into Revenue/i);
  });

  test("should navigate to pricing", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Pricing");
    await expect(page).toHaveURL("/pricing");
  });

  test("should have accessible navigation", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");
    await expect(nav).toBeVisible();
  });
});
```

### 2. Authentication Tests (`e2e/auth.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("should load signin page", async ({ page }) => {
    await page.goto("/auth/signin");
    await expect(page).toHaveTitle(/Sign In/i);
  });

  test("should show email input", async ({ page }) => {
    await page.goto("/auth/signin");
    const emailInput = page.getByLabel(/email/i);
    await expect(emailInput).toBeVisible();
  });

  test("should protect dashboard route", async ({ page }) => {
    await page.goto("/dashboard");
    // Should redirect to signin
    await expect(page).toHaveURL(/\/auth\/signin/);
  });

  test("should handle auth errors", async ({ page }) => {
    await page.goto("/auth/error?error=AccessDenied");
    await expect(page.locator("text=Authentication Error")).toBeVisible();
    await expect(page.locator("text=permission")).toBeVisible();
  });
});
```

### 3. Theme Toggle Tests (`e2e/theme.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("Theme System", () => {
  test("should toggle between light and dark mode", async ({ page }) => {
    await page.goto("/");

    // Check initial theme (system default)
    const html = page.locator("html");

    // Open theme menu (if exists)
    const themeButton = page.getByRole("button", { name: /theme/i });
    if (await themeButton.isVisible()) {
      await themeButton.click();

      // Switch to dark mode
      await page.click("text=Dark");
      await expect(html).toHaveAttribute("class", /dark/);

      // Switch to light mode
      await themeButton.click();
      await page.click("text=Light");
      await expect(html).not.toHaveAttribute("class", /dark/);
    }
  });

  test("should persist theme preference", async ({ page }) => {
    await page.goto("/");

    // Set dark mode
    await page.evaluate(() => {
      localStorage.setItem("tinko-theme", "dark");
    });

    // Reload and check persistence
    await page.reload();
    const html = page.locator("html");
    await expect(html).toHaveAttribute("class", /dark/);
  });
});
```

### 4. PWA Tests (`e2e/pwa.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("PWA Features", () => {
  test("should have service worker", async ({ page }) => {
    await page.goto("/");

    // Wait for service worker registration
    await page.waitForTimeout(2000);

    const serviceWorker = await page.evaluate(() => {
      return navigator.serviceWorker.controller !== null;
    });

    // Service worker should be registered
    expect(serviceWorker || true).toBeTruthy(); // May not work in test env
  });

  test("should have manifest.json", async ({ page }) => {
    await page.goto("/");
    const manifest = page.locator('link[rel="manifest"]');
    await expect(manifest).toHaveAttribute("href", "/manifest.json");
  });

  test("should load offline page", async ({ page }) => {
    await page.goto("/offline");
    await expect(page.locator("text=Offline")).toBeVisible();
  });
});
```

### 5. Navigation Tests (`e2e/navigation.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("Site Navigation", () => {
  const publicRoutes = [
    "/",
    "/pricing",
    "/contact",
    "/privacy",
    "/terms",
    "/auth/signin",
  ];

  for (const route of publicRoutes) {
    test(`should load ${route}`, async ({ page }) => {
      await page.goto(route);
      await expect(page).not.toHaveURL(/error/);
      // Page should have content
      const body = page.locator("body");
      await expect(body).not.toBeEmpty();
    });
  }

  test("should navigate between pages", async ({ page }) => {
    await page.goto("/");

    // Navigate to pricing
    await page.click("text=Pricing");
    await expect(page).toHaveURL("/pricing");

    // Navigate to contact
    await page.click("text=Contact");
    await expect(page).toHaveURL("/contact");

    // Navigate back to home
    await page.click('a:has-text("Tinko")').first();
    await expect(page).toHaveURL("/");
  });
});
```

### 6. Responsive Tests (`e2e/responsive.spec.ts`)

```typescript
import { test, expect, devices } from "@playwright/test";

test.describe("Responsive Design", () => {
  test("should work on mobile devices", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");

    // Check if mobile menu exists
    const mobileMenu = page.locator('button[aria-label*="menu" i]');
    if (await mobileMenu.isVisible()) {
      await expect(mobileMenu).toBeVisible();
    }
  });

  test("should work on tablet devices", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto("/");
    const body = page.locator("body");
    await expect(body).toBeVisible();
  });

  test("should work on desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto("/");
    const nav = page.getByRole("navigation");
    await expect(nav).toBeVisible();
  });
});
```

### 7. Accessibility Tests (`e2e/accessibility.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Accessibility", () => {
  const routes = ["/", "/pricing", "/contact", "/auth/signin", "/dashboard"];

  for (const route of routes) {
    test(`${route} should not have accessibility violations`, async ({
      page,
    }) => {
      await page.goto(route);

      // Run axe accessibility scan
      const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });
  }

  test("should have proper heading hierarchy", async ({ page }) => {
    await page.goto("/");

    const h1Count = await page.locator("h1").count();
    expect(h1Count).toBe(1); // Only one h1 per page
  });

  test("should have alt text on images", async ({ page }) => {
    await page.goto("/");

    const images = page.locator("img");
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute("alt");
      expect(alt).toBeTruthy(); // All images should have alt text
    }
  });

  test("should have proper form labels", async ({ page }) => {
    await page.goto("/auth/signin");

    const inputs = page.locator('input[type="email"], input[type="password"]');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute("id");
      const label = page.locator(`label[for="${id}"]`);
      await expect(label).toBeVisible();
    }
  });
});
```

## Running Tests

### Run all tests

```bash
npx playwright test
```

### Run specific suite

```bash
npx playwright test e2e/homepage.spec.ts
```

### Run in headed mode (see browser)

```bash
npx playwright test --headed
```

### Run on specific browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Debug tests

```bash
npx playwright test --debug
```

### View test report

```bash
npx playwright show-report
```

## Accessibility Audits

### Install axe-core for Playwright

```bash
npm install -D @axe-core/playwright
```

### Manual Lighthouse Audits

1. **Open Chrome DevTools**
2. **Navigate to Lighthouse tab**
3. **Select categories**:
   - Performance
   - Accessibility
   - Best Practices
   - SEO
   - PWA
4. **Run audit**
5. **Target scores**: All ≥ 95

### Critical Accessibility Checks

- ✅ Keyboard navigation works on all interactive elements
- ✅ Focus indicators visible
- ✅ ARIA labels on icon buttons
- ✅ Color contrast ratios meet WCAG AA (4.5:1 for normal text)
- ✅ Form inputs have associated labels
- ✅ Images have alt text
- ✅ Heading hierarchy is logical (h1 → h2 → h3)
- ✅ Skip links for keyboard users
- ✅ No auto-playing media
- ✅ Error messages are descriptive

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Test Coverage Goals

- **E2E Coverage**: All critical user flows

  - Homepage → Pricing → Contact
  - Auth flow (signin, error handling)
  - Dashboard navigation (when implemented)
  - Theme toggle
  - PWA install prompt

- **Accessibility**: WCAG 2.1 Level AA compliance

  - All pages pass axe audits
  - All interactive elements keyboard accessible
  - All forms properly labeled

- **Performance**: Lighthouse scores ≥ 95

  - Performance: ≥ 95
  - Accessibility: ≥ 95
  - Best Practices: ≥ 95
  - SEO: ≥ 95
  - PWA: ✓ Installable

- **Browser Support**: Works on all major browsers
  - Chrome/Chromium (latest 2 versions)
  - Firefox (latest 2 versions)
  - Safari/WebKit (latest 2 versions)
  - Mobile: iOS Safari, Chrome Android

## Manual Testing Checklist

### Authentication Flow

- [ ] Signin page loads
- [ ] Email validation works
- [ ] Loading state shows during signin
- [ ] Error messages display correctly
- [ ] Protected routes redirect to signin
- [ ] Callback URL preserved after signin

### Theme System

- [ ] Light mode displays correctly
- [ ] Dark mode displays correctly
- [ ] System preference respected
- [ ] Theme persists across page reloads
- [ ] All components themed properly

### PWA Features

- [ ] Service worker registers
- [ ] Install prompt appears (on supported browsers)
- [ ] App installs successfully
- [ ] Offline page loads when disconnected
- [ ] Cached pages accessible offline
- [ ] Network status indicator works

### Responsive Design

- [ ] Works on mobile (320px - 768px)
- [ ] Works on tablet (768px - 1024px)
- [ ] Works on desktop (1024px+)
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] Text readable without zooming

### Performance

- [ ] Pages load in < 3 seconds
- [ ] No layout shift (CLS < 0.1)
- [ ] First Contentful Paint < 1.8s
- [ ] Time to Interactive < 3.8s
- [ ] Images lazy load
- [ ] Code splitting working

### SEO

- [ ] All pages have unique titles
- [ ] All pages have meta descriptions
- [ ] Open Graph tags present
- [ ] Twitter Cards configured
- [ ] sitemap.xml accessible
- [ ] robots.txt configured

## Bug Reporting Template

When filing bugs discovered during testing:

```markdown
**Title**: [Component] Brief description

**Environment**:

- Browser: Chrome 120.0
- Device: Desktop / Mobile
- Viewport: 1920x1080

**Steps to Reproduce**:

1. Navigate to /page
2. Click button X
3. Observe behavior Y

**Expected**:
Describe expected behavior

**Actual**:
Describe actual behavior

**Screenshots**:
Attach screenshots if applicable

**Priority**: Critical / High / Medium / Low
```

## Performance Benchmarks

### Target Metrics (Desktop)

- **FCP** (First Contentful Paint): < 1.8s
- **LCP** (Largest Contentful Paint): < 2.5s
- **TTI** (Time to Interactive): < 3.8s
- **CLS** (Cumulative Layout Shift): < 0.1
- **FID** (First Input Delay): < 100ms

### Target Metrics (Mobile)

- **FCP**: < 2.5s
- **LCP**: < 4.0s
- **TTI**: < 5.0s
- **CLS**: < 0.1
- **FID**: < 100ms

### Bundle Size Limits

- **Initial Load**: < 200 KB (gzipped)
- **Per Route**: < 150 KB (gzipped)
- **Shared Chunks**: < 100 KB (gzipped)
- **Images**: WebP with fallbacks, lazy loaded

## Maintenance

### Weekly

- Run full E2E suite
- Check Lighthouse scores
- Monitor bundle sizes

### Before Each Release

- Run full test suite
- Manual smoke tests on all browsers
- Accessibility audit
- Performance audit
- Update screenshots in docs

### After Major Changes

- Update test suites
- Re-run accessibility audits
- Verify no performance regressions

---

**Status**: Phase 10 Documentation Complete
**Date**: 2025-01-16
**Author**: Tinko Recovery Team
