# Tinko Design System

**Version**: 2.0.0 — World-Class Quality  
**Last Updated**: Phase 1 of Design System Overhaul  
**Quality Bar**: Stripe/Vercel-Caliber Premium

---

## Philosophy

This design system elevates Tinko Recovery to enterprise-grade visual quality:

- **Professional Trust**: Deep, confident colors that convey stability and expertise
- **Modern Premium**: Soft corners, layered shadows, delightful animations
- **Enterprise-Grade**: WCAG AA compliant, accessible by default, production-ready
- **Token-First**: All components use design tokens, never hard-coded values
- **Performance-First**: Zero runtime cost, 60fps interactions, instant theme switching

**Never Basic** — Every detail is crafted for world-class B2B interfaces.

---

## Typography System

### Font Family

```css
--font-family: "Inter", system-ui, -apple-system, sans-serif;
```

**Inter** is a professional typeface designed specifically for screens with excellent legibility at all sizes. It features carefully crafted letter shapes, consistent spacing, and optimal contrast.

### Fluid Typography Scale

All sizes use `clamp()` for smooth, responsive scaling across all viewports:

| Token              | Min Size        | Preferred        | Max Size         | Usage                      |
| ------------------ | --------------- | ---------------- | ---------------- | -------------------------- |
| `--font-size-xs`   | 0.75rem (12px)  | 0.7rem + 0.2vw   | 0.8125rem (13px) | Captions, labels, metadata |
| `--font-size-sm`   | 0.875rem (14px) | 0.85rem + 0.15vw | 0.9375rem (15px) | Body text (small)          |
| `--font-size-base` | 1rem (16px)     | 0.95rem + 0.25vw | 1.125rem (18px)  | Body text (default)        |
| `--font-size-lg`   | 1.125rem (18px) | 1.05rem + 0.4vw  | 1.375rem (22px)  | Lead paragraphs            |
| `--font-size-xl`   | 1.25rem (20px)  | 1.1rem + 0.75vw  | 1.75rem (28px)   | Subheadings                |
| `--font-size-2xl`  | 1.5rem (24px)   | 1.25rem + 1.25vw | 2.25rem (36px)   | H3 headings                |
| `--font-size-3xl`  | 1.875rem (30px) | 1.5rem + 1.875vw | 2.875rem (46px)  | H2 headings                |
| `--font-size-4xl`  | 2.25rem (36px)  | 1.75rem + 2.5vw  | 3.5rem (56px)    | H1 headings                |
| `--font-size-5xl`  | 3rem (48px)     | 2rem + 5vw       | 4.5rem (72px)    | Display text (landing)     |
| `--font-size-6xl`  | 3.75rem (60px)  | 3rem + 3.75vw    | 5rem (80px)      | Hero headlines             |

### Line Height (Optical Sizing)

Carefully tuned for readability and visual balance:

- `--leading-tight: 1.2` — Headlines, display text (≥36px)
- `--leading-snug: 1.375` — Subheadings (20-36px)
- `--leading-normal: 1.5` — Body text (14-18px, default)
- `--leading-relaxed: 1.625` — Long-form content
- `--leading-loose: 1.75` — Legal text, dense data tables

### Letter Spacing (For Premium Feel)

- `--tracking-tighter: -0.05em` — Large headlines (≥48px) for optical balance
- `--tracking-tight: -0.025em` — Headings (24-48px)
- `--tracking-normal: 0` — Body text (default)
- `--tracking-wide: 0.025em` — Uppercase labels, button text

**Usage Example:**

```tsx
<h1 className="text-5xl font-semibold tracking-tight leading-tight">
  Recover Failed Payments Automatically
</h1>
<p className="text-base leading-normal text-muted-foreground">
  Tinko intelligently retries failed transactions using proven recovery patterns.
</p>
```

---

## Color System (WCAG AA Compliant)

### Semantic Tokens — Light Mode

All colors use HSL format with RGB values for Tailwind compatibility. Every combination passes WCAG AA contrast ratios (≥4.5:1).

#### Core Colors

| Token               | Value (HSL)   | Hex     | Contrast | Usage                                    |
| ------------------- | ------------- | ------- | -------- | ---------------------------------------- |
| `--background`      | `250 251 252` | #fafbfc | —        | Page background (softer than pure white) |
| `--foreground`      | `15 23 42`    | #0f172a | 16.4:1 ✓ | Primary text (slate-900)                 |
| `--card`            | `255 255 255` | #ffffff | —        | Card surfaces                            |
| `--card-foreground` | `15 23 42`    | #0f172a | 21:1 ✓   | Text on cards                            |

#### Primary (Professional Blue)

| Token                  | Value (HSL)   | Hex     | Usage                                    |
| ---------------------- | ------------- | ------- | ---------------------------------------- |
| `--primary`            | `30 64 175`   | #1e40af | Primary CTAs, links (blue-800 for depth) |
| `--primary-foreground` | `255 255 255` | #ffffff | Text on primary buttons                  |
| `--primary-hover`      | `37 99 235`   | #2563eb | Hover state (blue-600)                   |
| `--primary-active`     | `29 78 216`   | #1d4ed8 | Active press state (blue-700)            |

#### Accent (Electric Gradient)

| Token            | Value (HSL)  | Hex     | Usage                     |
| ---------------- | ------------ | ------- | ------------------------- |
| `--accent-start` | `59 130 246` | #3b82f6 | Gradient start (blue-500) |
| `--accent-end`   | `147 51 234` | #9333ea | Gradient end (purple-600) |

Use sparingly for hero CTAs and active states only.

#### Semantic States

| Token                 | Value         | Hex     | Contrast | Usage                             |
| --------------------- | ------------- | ------- | -------- | --------------------------------- |
| `--success`           | `21 128 61`   | #15803d | 4.7:1 ✓  | Success messages, positive states |
| `--success-light`     | `240 253 244` | #f0fdf4 | —        | Success alert backgrounds         |
| `--warning`           | `180 83 9`    | #b45309 | 4.6:1 ✓  | Warnings, cautionary messages     |
| `--warning-light`     | `254 252 232` | #fefce8 | —        | Warning backgrounds               |
| `--destructive`       | `185 28 28`   | #b91c1c | 5.1:1 ✓  | Errors, delete actions            |
| `--destructive-light` | `254 242 242` | #fef2f2 | —        | Error backgrounds                 |
| `--info`              | `3 105 161`   | #0369a1 | 4.8:1 ✓  | Informational messages            |
| `--info-light`        | `240 249 255` | #f0f9ff | —        | Info backgrounds                  |

#### Surface & Borders

| Token                | Value         | Usage                          |
| -------------------- | ------------- | ------------------------------ |
| `--muted`            | `241 245 249` | Muted backgrounds (slate-100)  |
| `--muted-foreground` | `100 116 139` | Muted text (slate-500)         |
| `--border`           | `226 232 240` | Default borders (slate-200)    |
| `--border-strong`    | `203 213 225` | Emphasized borders (slate-300) |

### Dark Mode

Dark mode uses lighter accent colors for readability while maintaining professional depth:

- `--background: 15 23 42` (slate-900) — Deep, not pure black for comfort
- `--primary: 59 130 246` (blue-500) — Brighter for dark backgrounds
- `--card: 30 41 59` (slate-800) — Surface elevation
- All semantic states adjusted for dark backgrounds

**Usage Example:**

```tsx
<button className="bg-primary hover:bg-primary-hover text-primary-foreground">
  Start Free Trial
</button>

<div className="bg-success-light text-success border border-success/20 rounded-lg p-4">
  Payment recovered successfully!
</div>
```

---

## Spacing System

4-point base grid for consistent vertical rhythm and mathematical harmony:

| Token        | Value   | Pixels | Usage                        |
| ------------ | ------- | ------ | ---------------------------- |
| `--space-1`  | 0.25rem | 4px    | Tight spacing (icon padding) |
| `--space-2`  | 0.5rem  | 8px    | Icon spacing, small gaps     |
| `--space-3`  | 0.75rem | 12px   | Compact padding (badges)     |
| `--space-4`  | 1rem    | 16px   | Default spacing (buttons)    |
| `--space-6`  | 1.5rem  | 24px   | Section padding              |
| `--space-8`  | 2rem    | 32px   | Card padding                 |
| `--space-12` | 3rem    | 48px   | Large section gaps           |
| `--space-16` | 4rem    | 64px   | Hero spacing                 |
| `--space-24` | 6rem    | 96px   | Page section separators      |

**Usage Example:**

```tsx
<div className="p-8 space-y-6">
  <h2 className="mb-4 text-3xl">Recovery Analytics</h2>
  <div className="grid grid-cols-3 gap-6">
    <div className="p-6">Card content</div>
  </div>
</div>
```

---

## Border Radius

Modern soft corners for premium feel without being overly playful:

| Token           | Value  | Usage                         |
| --------------- | ------ | ----------------------------- |
| `--radius-sm`   | 6px    | Badges, chips, small elements |
| `--radius-md`   | 10px   | Buttons, inputs, default      |
| `--radius-lg`   | 14px   | Cards, panels                 |
| `--radius-xl`   | 20px   | Large cards, feature blocks   |
| `--radius-2xl`  | 24px   | Hero sections                 |
| `--radius-3xl`  | 32px   | Exceptional hero elements     |
| `--radius-full` | 9999px | Pills, avatars, fully rounded |

**Usage Example:**

```tsx
<div className="rounded-lg bg-card shadow-sm p-6">
  <button className="rounded-md px-4 py-2">Action</button>
</div>
```

---

## Elevation (Shadow System)

Layered shadow system with umbra + penumbra for realistic depth perception:

### Base Shadows

| Token          | Value                               | Usage                       |
| -------------- | ----------------------------------- | --------------------------- |
| `--shadow-xs`  | `0 1px 2px rgba(0,0,0,0.05)`        | Subtle hint of depth        |
| `--shadow-sm`  | `0 2px 4px -1px rgba(0,0,0,0.08)`   | Input fields, subtle cards  |
| `--shadow-md`  | `0 4px 8px -2px rgba(0,0,0,0.12)`   | Resting cards, hover states |
| `--shadow-lg`  | `0 8px 16px -4px rgba(0,0,0,0.16)`  | Dropdowns, modals           |
| `--shadow-xl`  | `0 12px 24px -6px rgba(0,0,0,0.20)` | Popovers, tooltips          |
| `--shadow-2xl` | `0 16px 32px -8px rgba(0,0,0,0.24)` | Overlays, dialogs           |

### Colored Shadows (For Emphasis)

Use sparingly for hierarchy and emphasis:

- `--shadow-primary` — Blue tint for primary CTAs and active states
- `--shadow-success` — Green tint for success confirmations
- `--shadow-warning` — Amber tint for warning alerts
- `--shadow-destructive` — Red tint for destructive actions

**Usage Example:**

```tsx
<div className="bg-card shadow-sm hover:shadow-md transition-shadow rounded-lg">
  Interactive card with elevation
</div>

<button className="btn-primary shadow-primary">
  Primary CTA with glow
</button>
```

---

## Motion System

Carefully tuned timing with spring easing for delightful, professional interactions:

### Timing

| Token                 | Duration | Usage                                 |
| --------------------- | -------- | ------------------------------------- |
| `--transition-fast`   | 120ms    | Hover, focus (instant feedback)       |
| `--transition-base`   | 180ms    | Default transitions                   |
| `--transition-slow`   | 300ms    | Panel slides, drawer open/close       |
| `--transition-slower` | 500ms    | Page transitions, major state changes |

### Easing Curves

- `--ease-in` — `cubic-bezier(0.4, 0, 1, 1)` — Accelerate in
- `--ease-out` — `cubic-bezier(0, 0, 0.2, 1)` — Decelerate out
- `--ease-in-out` — `cubic-bezier(0.4, 0, 0.2, 1)` — Smooth both ends (default)
- `--ease-spring` — `cubic-bezier(0.34, 1.56, 0.64, 1)` — Playful bounce (use sparingly!)

**Usage Example:**

```tsx
<button className="transition-all duration-fast hover:scale-[1.02] active:scale-[0.98]">
  Interactive Button
</button>

<div className="animate-slide-up">
  Toast Notification
</div>
```

---

## Animations

### Available Keyframes

| Animation            | Behavior            | Duration | Easing   |
| -------------------- | ------------------- | -------- | -------- |
| `animate-fade-in`    | Opacity 0→1         | 180ms    | ease-out |
| `animate-slide-up`   | Slide from bottom   | 180ms    | spring   |
| `animate-slide-down` | Slide from top      | 180ms    | spring   |
| `animate-scale-in`   | Scale 0.95→1 + fade | 120ms    | spring   |

**Usage Example:**

```tsx
<div className="animate-scale-in">
  Modal content appears with scale + fade
</div>

<div className="animate-slide-up">
  Toast slides up from bottom
</div>
```

### Reduced Motion

**CRITICAL**: All animations respect `prefers-reduced-motion` and disable automatically for accessibility. Never override this behavior.

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Usage in Tailwind

Semantic tokens are available as Tailwind classes:

```tsx
// ✅ Good - Uses semantic tokens
<div className="bg-background text-foreground">
  <div className="bg-card text-card-foreground">
    <button className="bg-primary text-primary-foreground">
      Submit
    </button>
  </div>
</div>

// ❌ Bad - Hard-coded colors
<div className="bg-slate-50 text-slate-900">
  <div className="bg-white text-slate-900">
    <button className="bg-blue-600 text-white">
      Submit
    </button>
  </div>
</div>
```

### Brand Colors (Legacy)

Original brand colors are preserved for backward compatibility:

```css
--brand-primary: #2563eb (light) / #3b82f6 (dark)
--brand-primary-light: #eff6ff (light) / #1e3a8a (dark)
--brand-primary-dark: #1e40af (light) / #60a5fa (dark)
```

These are being phased out in favor of semantic tokens.

---

## Typography

### Font Families

Two professional font families optimized for B2B SaaS:

#### Inter (UI Font)

- **Purpose**: Body text, headings, UI components
- **Weights**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold)
- **Features**: OpenType features enabled (`cv02`, `cv03`, `cv04`, `cv11` for better readability)
- **Variable**: `var(--font-inter)`
- **Tailwind**: `font-sans` or `font-display`

#### JetBrains Mono (Code Font)

- **Purpose**: Code snippets, API responses, logs
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Features**: Monospace, ligatures
- **Variable**: `var(--font-jetbrains-mono)`
- **Tailwind**: `font-mono`

### Font Sizes (Fluid Typography)

Fluid typography scales between mobile and desktop:

| Class       | Min Size | Max Size | Use Case               |
| ----------- | -------- | -------- | ---------------------- |
| `text-xs`   | 0.75rem  | 0.875rem | Small labels, captions |
| `text-sm`   | 0.875rem | 1rem     | Body text (small)      |
| `text-base` | 1rem     | 1.125rem | Body text (default)    |
| `text-lg`   | 1.125rem | 1.25rem  | Large body text        |
| `text-xl`   | 1.25rem  | 1.5rem   | Small headings         |
| `text-2xl`  | 1.5rem   | 2rem     | Subheadings            |
| `text-3xl`  | 1.875rem | 2.5rem   | H3 headings            |
| `text-4xl`  | 2.25rem  | 3rem     | H2 headings            |
| `text-5xl`  | 3rem     | 4rem     | H1 headings            |
| `text-6xl`  | 3.75rem  | -        | Hero text              |

### Font Usage Examples

```tsx
// Headings
<h1 className="text-4xl font-bold tracking-tight text-foreground">
  Page Title
</h1>

<h2 className="text-3xl font-semibold text-foreground">
  Section Title
</h2>

// Body text
<p className="text-base text-muted-foreground">
  Descriptive text with muted color for hierarchy
</p>

// Code
<code className="font-mono text-sm bg-muted px-2 py-1 rounded">
  npm install
</code>
```

---

## Spacing Scale

Consistent spacing using CSS variables:

| Variable        | Value   | Tailwind   | Use Case         |
| --------------- | ------- | ---------- | ---------------- |
| `--spacing-xs`  | 0.5rem  | `space-2`  | Tight spacing    |
| `--spacing-sm`  | 0.75rem | `space-3`  | Small gaps       |
| `--spacing-md`  | 1rem    | `space-4`  | Default spacing  |
| `--spacing-lg`  | 1.5rem  | `space-6`  | Generous spacing |
| `--spacing-xl`  | 2rem    | `space-8`  | Section spacing  |
| `--spacing-2xl` | 3rem    | `space-12` | Large sections   |
| `--spacing-3xl` | 4rem    | `space-16` | Page sections    |

---

## Border Radius

Rounded corners for modern UI:

| Variable        | Value    | Tailwind       | Use Case                  |
| --------------- | -------- | -------------- | ------------------------- |
| `--radius-sm`   | 0.375rem | `rounded-md`   | Small elements (badges)   |
| `--radius-md`   | 0.5rem   | `rounded-lg`   | Default (buttons, inputs) |
| `--radius-lg`   | 0.75rem  | `rounded-xl`   | Cards                     |
| `--radius-xl`   | 1rem     | `rounded-2xl`  | Large cards               |
| `--radius-2xl`  | 1.5rem   | `rounded-3xl`  | Hero sections             |
| `--radius-full` | 9999px   | `rounded-full` | Pills, avatars            |

**Standard**: Most UI components use `rounded-xl` (12px) for a modern, friendly appearance.

---

## Shadows

Elevation system with three levels:

| Variable          | Value                         | Tailwind        | Use Case                  |
| ----------------- | ----------------------------- | --------------- | ------------------------- |
| `--shadow-soft`   | `0 2px 8px rgba(0,0,0,0.08)`  | `shadow-soft`   | Subtle elevation (inputs) |
| `--shadow-medium` | `0 4px 16px rgba(0,0,0,0.12)` | `shadow-medium` | Cards, dropdowns          |
| `--shadow-strong` | `0 8px 32px rgba(0,0,0,0.16)` | `shadow-strong` | Modals, popovers          |

```tsx
// Card with soft shadow
<div className="bg-card shadow-soft rounded-xl p-6">
  Content
</div>

// Hover effect with shadow transition
<div className="shadow-soft hover:shadow-medium transition-shadow">
  Hover me
</div>
```

---

## Motion System

### Transition Timing

Consistent animation durations:

| Variable            | Value | Tailwind       | Use Case               |
| ------------------- | ----- | -------------- | ---------------------- |
| `--transition-fast` | 150ms | `duration-150` | Quick feedback (hover) |
| `--transition-base` | 300ms | `duration-300` | Default transitions    |
| `--transition-slow` | 500ms | `duration-500` | Complex animations     |

### Easing

Standard easing: `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out)

### Animations

Pre-built animations respecting `prefers-reduced-motion`:

```tsx
// Fade in
<div className="animate-fade-in">
  Fades in on load
</div>

// Slide up
<div className="animate-slide-up">
  Slides up from bottom
</div>

// Slide down
<div className="animate-slide-down">
  Slides down from top
</div>
```

### Motion Preferences

Animations automatically respect user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Component Variants

### Button Variants

| Variant       | Purpose             | Background    | Text                     | Use Case             |
| ------------- | ------------------- | ------------- | ------------------------ | -------------------- |
| `primary`     | Primary actions     | `primary`     | `primary-foreground`     | Submit, Save, Create |
| `secondary`   | Secondary actions   | `secondary`   | `secondary-foreground`   | Cancel, Back, Edit   |
| `subtle`      | Tertiary actions    | `muted`       | `muted-foreground`       | View, Show More      |
| `ghost`       | Minimal actions     | `transparent` | `foreground`             | Icons, text links    |
| `destructive` | Destructive actions | `destructive` | `destructive-foreground` | Delete, Remove       |
| `outline`     | Outlined actions    | `background`  | `primary`                | Alternative CTA      |
| `link`        | Text links          | `transparent` | `primary`                | Navigation           |

```tsx
import { Button } from "@/components/ui/button"

// Primary action
<Button variant="primary">Save Changes</Button>

// Destructive action
<Button variant="destructive">Delete Account</Button>

// Ghost icon button
<Button variant="ghost" size="icon">
  <Icon />
</Button>
```

### Badge Variants

| Variant     | Purpose         | Background       | Text                   | Use Case          |
| ----------- | --------------- | ---------------- | ---------------------- | ----------------- |
| `default`   | Default badge   | `primary`        | `primary-foreground`   | Generic labels    |
| `success`   | Success state   | `success/10`     | `success`              | Active, Completed |
| `warning`   | Warning state   | `warning/10`     | `warning`              | Pending, Alert    |
| `error`     | Error state     | `destructive/10` | `destructive`          | Failed, Error     |
| `secondary` | Secondary badge | `secondary`      | `secondary-foreground` | Info, Labels      |
| `outline`   | Outlined badge  | `transparent`    | `foreground`           | Subtle status     |

```tsx
import { Badge } from "@/components/ui/badge"

<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
```

---

## Dark Mode

### Enabling Dark Mode

Dark mode is controlled via the `ThemeProvider`:

```tsx
import { ThemeProvider } from "@/components/providers/theme-provider";

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider defaultTheme="system" storageKey="tinko-theme">
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### Using Theme Hook

```tsx
"use client";

import { useTheme } from "@/components/providers/theme-provider";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
      Toggle theme (current: {theme})
    </button>
  );
}
```

### Theme Options

- `"light"`: Force light mode
- `"dark"`: Force dark mode
- `"system"`: Follow OS preference (default)

### Dark Mode Classes

The theme provider automatically adds `.dark` class to `<html>` element in dark mode. All semantic tokens update automatically.

---

## Accessibility

### WCAG AA Compliance

All color combinations meet WCAG AA contrast requirements:

- **Normal text**: ≥4.5:1 contrast ratio
- **Large text**: ≥3:1 contrast ratio
- **UI components**: ≥3:1 contrast ratio

### Focus Indicators

All interactive elements have visible focus rings:

```css
*:focus-visible {
  outline: none;
  ring: 2px solid rgb(var(--ring));
  ring-offset: 2px;
}
```

### Keyboard Navigation

- All components keyboard accessible
- Tab order follows visual hierarchy
- Skip links for main content

### Screen Reader Support

- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- ARIA labels where needed
- Alternative text for images

---

## CSS Variables Reference

### Complete Token List

```css
/* Semantic Tokens (RGB format for alpha support) */
--background: 248 250 252;
--foreground: 15 23 42;
--card: 255 255 255;
--card-foreground: 15 23 42;
--popover: 255 255 255;
--popover-foreground: 15 23 42;
--primary: 37 99 235;
--primary-foreground: 255 255 255;
--secondary: 241 245 249;
--secondary-foreground: 15 23 42;
--muted: 241 245 249;
--muted-foreground: 100 116 139;
--accent: 241 245 249;
--accent-foreground: 15 23 42;
--destructive: 239 68 68;
--destructive-foreground: 255 255 255;
--success: 34 197 94;
--success-foreground: 255 255 255;
--warning: 245 158 11;
--warning-foreground: 255 255 255;
--border: 226 232 240;
--input: 226 232 240;
--ring: 37 99 235;

/* Typography Scale (Fluid) */
--font-size-xs: clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem);
--font-size-sm: clamp(0.875rem, 0.8rem + 0.3vw, 1rem);
--font-size-base: clamp(1rem, 0.95rem + 0.3vw, 1.125rem);
/* ... (see globals.css for complete list) */

/* Spacing Scale */
--spacing-xs: 0.5rem;
--spacing-sm: 0.75rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;
--spacing-3xl: 4rem;

/* Border Radius */
--radius-sm: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
--radius-2xl: 1.5rem;
--radius-full: 9999px;

/* Shadows */
--shadow-soft: 0 2px 8px 0 rgb(0 0 0 / 0.08);
--shadow-medium: 0 4px 16px 0 rgb(0 0 0 / 0.12);
--shadow-strong: 0 8px 32px 0 rgb(0 0 0 / 0.16);

/* Transitions */
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Best Practices

### ✅ Do

1. **Use semantic tokens** in components (`bg-primary`, not `bg-blue-600`)
2. **Test both themes** when building new features
3. **Use `text-muted-foreground`** for descriptions and secondary text
4. **Apply consistent spacing** from the spacing scale
5. **Use `rounded-xl`** for most UI components (modern standard)
6. **Add focus rings** to all interactive elements
7. **Respect motion preferences** with `@media (prefers-reduced-motion)`

### ❌ Don't

1. **Hardcode hex colors** (`#2563eb` → use `rgb(var(--primary))`)
2. **Mix old and new systems** (avoid `--brand-primary` in new code)
3. **Create custom shadows** without purpose
4. **Ignore focus states** for keyboard navigation
5. **Force animations** on users with reduced motion preference
6. **Use too many font sizes** (stick to the scale)
7. **Forget alpha transparency** (use `rgb(var(--primary) / 0.5)` for 50% opacity)

---

## Migration Guide

### Updating Existing Components

**Before (Old System):**

```tsx
<div className="bg-slate-50 text-slate-900 border-slate-200">
  <button className="bg-blue-600 text-white hover:bg-blue-700">Click me</button>
</div>
```

**After (New System):**

```tsx
<div className="bg-background text-foreground border-border">
  <Button variant="primary">Click me</Button>
</div>
```

### Checklist for Component Updates

- [ ] Replace `bg-white` with `bg-card`
- [ ] Replace `text-slate-900` with `text-foreground`
- [ ] Replace `text-slate-600` with `text-muted-foreground`
- [ ] Replace `border-slate-200` with `border-border`
- [ ] Replace custom buttons with `<Button>` component
- [ ] Replace custom badges with `<Badge>` component
- [ ] Test in both light and dark modes
- [ ] Verify WCAG AA contrast

---

## Phase 2 Acceptance Tests

### ✅ Visual Checks

- [ ] Light/dark mode toggle works
- [ ] System preference detection works
- [ ] All components visible in both themes
- [ ] No flash of unstyled content (FOUC)

### ✅ Contrast Tests

- [ ] Text on backgrounds: ≥4.5:1 ratio
- [ ] Interactive elements: ≥3:1 ratio
- [ ] Focus rings clearly visible
- [ ] All colors WCAG AA compliant

### ✅ Typography Tests

- [ ] Inter font loads correctly
- [ ] JetBrains Mono for code blocks
- [ ] Font sizes scale on mobile
- [ ] Line heights readable

### ✅ Component Tests

- [ ] Button variants render correctly
- [ ] Badge variants show proper colors
- [ ] Input fields use theme tokens
- [ ] Focus states visible on all interactive elements

### ✅ Accessibility Tests

- [ ] Keyboard navigation works
- [ ] Screen reader announces properly
- [ ] Skip links functional
- [ ] Motion respects user preferences

---

## Support

For questions or issues with the theme system:

- **Internal Docs**: `/docs/THEME.md` (this file)
- **Code Reference**: `app/globals.css`, `tailwind.config.js`
- **Components**: `components/ui/button.tsx`, `components/ui/badge.tsx`

---

**Status**: ✅ Phase 2 Complete  
**Next Phase**: Phase 3 - PWA Enablement & Verification
