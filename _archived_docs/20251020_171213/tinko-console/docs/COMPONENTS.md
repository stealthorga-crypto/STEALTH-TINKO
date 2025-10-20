# Component Library Documentation

Complete reference for all Tinko UI components with Stripe/Vercel-caliber quality.

## Table of Contents

1. [Buttons](#buttons)
2. [Forms](#forms)
3. [Cards & Surfaces](#cards--surfaces)
4. [Data Display](#data-display)
5. [Feedback](#feedback)
6. [Layout](#layout)
7. [States](#states)

---

## Buttons

### Button

Primary interactive component with 7 variants, multiple sizes, loading state, and full accessibility.

**Variants:**

- `primary` (default) - Main CTAs with colored background
- `secondary` - Secondary actions with subtle styling
- `subtle` - Low-emphasis actions
- `ghost` - Minimal styling, transparent background
- `destructive` - Dangerous/delete actions in red
- `outline` - Outlined variant for secondary prominence
- `link` - Link-styled button

**Sizes:**

- `sm` - Small (h-9, px-3, text-xs)
- `default` - Standard (h-10, px-4)
- `lg` - Large (h-12, px-6, text-base)
- `icon` - Icon-only (size-10)
- `icon-sm` - Small icon (size-9)
- `icon-lg` - Large icon (size-12)

**Props:**

- `loading?: boolean` - Shows spinner, disables interaction
- All standard button attributes

**Usage:**

```tsx
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

// Primary CTA
<Button variant="primary">Save Changes</Button>

// With icon
<Button variant="secondary">
  <Plus className="size-5" />
  Add Rule
</Button>

// Loading state
<Button variant="primary" loading={isSubmitting}>
  Submit
</Button>

// Icon-only
<Button variant="ghost" size="icon" aria-label="Delete">
  <Trash className="size-5" />
</Button>

// Destructive action
<Button variant="destructive">
  Delete Account
</Button>
```

**States:**

- **Hover**: Darker background, elevated shadow
- **Active**: Scale down (0.98), darker background
- **Focus**: 2px primary ring, 2px offset
- **Disabled**: 50% opacity, no pointer events
- **Loading**: Spinner icon, disabled state

**Accessibility:**

- Focus ring always visible (outline-offset: 2px)
- Active scale provides tactile feedback
- Loading state announces "Loading" to screen readers
- Icon-only buttons require aria-label

---

## Forms

### Input

Text input with validation states (default, error, success) and full accessibility.

**Props:**

- `error?: boolean` - Red border, error ring
- `success?: boolean` - Green border, success ring
- All standard input attributes

**Usage:**

```tsx
import { Input } from "@/components/ui/input"

// Basic
<Input type="email" placeholder="you@company.com" />

// Error state
<Input
  type="email"
  error
  aria-describedby="email-error"
/>
<span id="email-error" className="text-xs text-destructive">
  Please enter a valid email
</span>

// Success state
<Input
  type="email"
  success
  defaultValue="you@company.com"
/>
```

**States:**

- **Default**: Gray border, primary focus ring
- **Error**: Red border, red focus ring, aria-invalid
- **Success**: Green border, green focus ring
- **Disabled**: Muted background, 50% opacity, no pointer events
- **Focus**: 2px ring, 2px outline offset

### Label

Accessible form label with required indicator.

**Usage:**

```tsx
import { Label } from "@/components/ui/label"

<Label htmlFor="email">Email Address</Label>
<Input id="email" type="email" />

// With required indicator
<Label htmlFor="password" required>Password</Label>
```

### Textarea

Multi-line text input with auto-resize option.

**Props:**

- `error?: boolean`
- `success?: boolean`
- `autoResize?: boolean` - Expands to fit content
- All standard textarea attributes

**Usage:**

```tsx
import { Textarea } from "@/components/ui/textarea"

// Basic
<Textarea placeholder="Enter your message" />

// Auto-resize
<Textarea autoResize placeholder="Expands as you type" />

// Error state
<Textarea error aria-describedby="message-error" />
```

### FormField

Accessible form field with label, input/textarea, description, and error message.

**Usage:**

```tsx
import {
  FormField,
  FormLabel,
  FormInput,
  FormTextarea,
  FormDescription,
  FormError
} from "@/components/ui/form-field"

<FormField error={!!errors.email} errorMessage={errors.email}>
  <FormLabel required>Email Address</FormLabel>
  <FormInput type="email" placeholder="you@company.com" />
  <FormDescription>
    We'll never share your email with anyone else.
  </FormDescription>
  <FormError />
</FormField>

// With textarea
<FormField error={!!errors.bio} errorMessage={errors.bio}>
  <FormLabel>Bio</FormLabel>
  <FormTextarea autoResize placeholder="Tell us about yourself" />
  <FormError />
</FormField>
```

**Features:**

- Auto-generates unique ID for accessibility
- Links error messages via aria-describedby
- Required indicator on label
- Contextual error/success styling

---

## Cards & Surfaces

### Card

Flexible container with header, content, footer sections. Supports multiple variants and interactive states.

**Variants:**

- `default` - Standard with border and shadow
- `elevated` - Higher elevation, no border
- `outlined` - Border only, no shadow
- `ghost` - No border, no shadow

**Props:**

- `variant?: "default" | "elevated" | "outlined" | "ghost"`
- `interactive?: boolean` - Adds hover effects and cursor pointer

**Usage:**

```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"

// Standard card
<Card>
  <CardHeader>
    <CardTitle>Recovery Rate</CardTitle>
    <CardDescription>Last 30 days</CardDescription>
  </CardHeader>
  <CardContent>
    <p className="text-3xl font-bold">65%</p>
  </CardContent>
  <CardFooter>
    <Button variant="secondary">View Details</Button>
  </CardFooter>
</Card>

// Interactive card (clickable)
<Card variant="elevated" interactive onClick={() => console.log('clicked')}>
  <CardHeader>
    <CardTitle>Failed Payments</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-2xl font-bold">1,234</p>
  </CardContent>
</Card>
```

### Dialog (Modal)

Modal overlay with backdrop, close button, and focus trap.

**Usage:**

```tsx
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

<Dialog>
  <DialogTrigger>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Deletion</DialogTitle>
      <DialogDescription>
        This action cannot be undone. Are you sure you want to delete this rule?
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="secondary">Cancel</Button>
      <Button variant="destructive">Delete</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>;
```

**Features:**

- Backdrop overlay with blur
- Scale-in animation (zoom-in-95)
- ESC key closes dialog
- Click outside closes dialog
- Focus trap (can't tab outside)
- Body scroll lock when open

### Popover

Floating overlay positioned relative to trigger element.

**Usage:**

```tsx
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";

<Popover>
  <PopoverTrigger>
    <Button variant="secondary">Open Popover</Button>
  </PopoverTrigger>
  <PopoverContent>
    <div className="space-y-space-2">
      <h4 className="font-semibold">Quick Actions</h4>
      <p className="text-sm text-muted-foreground">Choose an action below</p>
    </div>
  </PopoverContent>
</Popover>;
```

**Features:**

- Auto-positioning (prevents overflow)
- Slide-in animation from trigger direction
- Click outside closes
- ESC key closes

### Tooltip

Accessible tooltip with hover delay and keyboard support.

**Usage:**

```tsx
import {
  TooltipProvider,
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { Info } from "lucide-react";

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>
      <Button variant="ghost" size="icon" aria-label="More information">
        <Info className="size-5" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>This shows additional information</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>;
```

**Features:**

- 500ms hover delay (prevents accidental triggers)
- Keyboard accessible (focus to show)
- Respects prefers-reduced-motion
- Auto-positioning

---

## Data Display

### Badge

Small status indicator with multiple variants and removable option.

**Variants:**

- `default` - Primary color
- `success` - Green for positive states
- `warning` - Amber for caution
- `destructive` - Red for errors
- `info` - Blue for informational
- `secondary` - Neutral gray
- `outline` - Border only

**Sizes:**

- `sm` - Small (px-2, py-0.5, text-xs)
- `default` - Standard (px-3, py-1, text-xs)
- `lg` - Large (px-4, py-1.5, text-sm)

**Props:**

- `removable?: boolean` - Adds X button
- `onRemove?: () => void` - Callback when X clicked

**Usage:**

```tsx
import { Badge } from "@/components/ui/badge"

// Status indicators
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="destructive">Failed</Badge>

// Removable (for filters/tags)
<Badge variant="secondary" removable onRemove={() => console.log('removed')}>
  Stripe
</Badge>

// Sizes
<Badge size="sm" variant="info">Beta</Badge>
<Badge size="lg" variant="default">Premium</Badge>
```

### Skeleton

Loading placeholder with shimmer animation.

**Components:**

- `Skeleton` - Basic block
- `SkeletonText` - Multiple lines
- `SkeletonCard` - Full card structure
- `SkeletonTable` - Table with rows

**Usage:**

```tsx
import { Skeleton, SkeletonText, SkeletonCard, SkeletonTable } from "@/components/ui/skeleton"

// Basic blocks
<Skeleton className="h-10 w-full" />
<Skeleton className="h-4 w-32" />

// Text with multiple lines
<SkeletonText lines={3} />

// Full card
<SkeletonCard />

// Table
<SkeletonTable rows={5} />
```

---

## Feedback

### Banner

Full-width alert with icon, message, and optional dismiss button.

**Variants:**

- `info` (default) - Blue for informational
- `success` - Green for success
- `warning` - Amber for warnings
- `destructive` - Red for errors

**Props:**

- `onDismiss?: () => void` - Makes dismissible

**Usage:**

```tsx
import { Banner } from "@/components/ui/banner"

// Info banner
<Banner variant="info">
  New features are available! Check out the changelog.
</Banner>

// Dismissible warning
<Banner variant="warning" onDismiss={() => console.log('dismissed')}>
  Your trial ends in 3 days. Upgrade to continue using premium features.
</Banner>

// Error banner
<Banner variant="destructive">
  Failed to connect to payment gateway. Please check your API keys.
</Banner>
```

### InlineAlert

Smaller inline alert for contextual messages within forms or sections.

**Usage:**

```tsx
import { InlineAlert } from "@/components/ui/banner";

<FormField>
  <FormLabel>API Key</FormLabel>
  <FormInput type="password" />
  <InlineAlert variant="warning">
    Never share your API key with anyone.
  </InlineAlert>
</FormField>;
```

---

## Layout

### PageHeader

Page title, description, and action buttons in consistent layout.

**Usage:**

```tsx
import { PageHeader, PageTitle, PageDescription } from "@/components/ui/layout";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

<PageHeader
  actions={
    <Button variant="primary">
      <Plus className="size-5" />
      Create Rule
    </Button>
  }
>
  <PageTitle>Recovery Rules</PageTitle>
  <PageDescription>
    Configure automated retry logic and customer notifications for failed
    payments.
  </PageDescription>
</PageHeader>;
```

### Section

Semantic section with consistent spacing.

**Usage:**

```tsx
import {
  Section,
  SectionHeader,
  SectionTitle,
  SectionDescription,
} from "@/components/ui/layout";

<Section>
  <SectionHeader>
    <SectionTitle>Active Rules</SectionTitle>
    <SectionDescription>
      Rules currently running for your payment flows.
    </SectionDescription>
  </SectionHeader>
  {/* Section content */}
</Section>;
```

### Container

Responsive container with max-width constraints.

**Sizes:**

- `sm` - max-w-2xl (672px)
- `md` - max-w-4xl (896px)
- `lg` - max-w-6xl (1152px)
- `xl` (default) - max-w-7xl (1280px)
- `2xl` - max-w-screen-2xl (1536px)
- `full` - No max-width

**Usage:**

```tsx
import { Container } from "@/components/ui/layout"

// Standard page container
<Container>
  <PageHeader>...</PageHeader>
  {/* Page content */}
</Container>

// Narrow container for text-heavy content
<Container size="md">
  <article>...</article>
</Container>

// Full width
<Container size="full">
  <div className="grid grid-cols-12">...</div>
</Container>
```

**Features:**

- Responsive padding: px-4 (mobile) → px-6 (tablet) → px-8 (desktop)
- Centered with mx-auto
- 100% width up to max-width

---

## States

### EmptyState

Placeholder for empty data with icon, message, and optional CTA.

**Usage:**

```tsx
import { EmptyState } from "@/components/states/empty-state";
import { Button } from "@/components/ui/button";
import { Inbox } from "lucide-react";

<EmptyState
  icon={Inbox}
  title="No recovery attempts yet"
  description="Failed payments will appear here once you integrate Tinko with your payment gateway."
  action={<Button variant="primary">Connect Payment Gateway</Button>}
/>;
```

**Features:**

- Centered layout with icon in muted circle
- Dashed border for visual differentiation
- Optional CTA button
- Accessible with proper ARIA

### ErrorState

Error display with icon, title, description, and retry action.

**Usage:**

```tsx
import { ErrorState } from "@/components/states/error-state";
import { Button } from "@/components/ui/button";

<ErrorState
  title="Failed to load data"
  description="We couldn't connect to the server. Please check your internet connection and try again."
  action={
    <Button variant="secondary" onClick={retry}>
      Retry
    </Button>
  }
/>;
```

**Features:**

- Red border and background (destructive variant)
- Alert icon in circle
- role="alert" for screen readers
- Optional retry button

### LoadingState

Loading placeholder with skeleton shimmer.

**Usage:**

```tsx
import { LoadingState } from "@/components/states/loading-state";

<LoadingState label="Loading recovery attempts" />;
```

**Features:**

- Skeleton blocks with pulse animation
- Screen reader announcement
- Consistent with other skeleton components

---

## Design Token Usage

All components use design tokens exclusively:

**Colors:**

- `primary`, `primary-hover`, `primary-active`
- `secondary`, `destructive`, `success`, `warning`, `info`
- `muted`, `accent`, `border`, `background`, `foreground`

**Spacing:**

- `space-1` (4px) through `space-24` (96px)
- Example: `px-space-4 py-space-2` instead of `px-4 py-2`

**Typography:**

- Font sizes: `text-xs` to `text-6xl` (use token variables)
- Line heights: `leading-tight`, `leading-normal`, `leading-loose`
- Letter spacing: `tracking-tighter`, `tracking-tight`, `tracking-wide`

**Shadows:**

- `shadow-xs`, `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-2xl`
- Colored: `shadow-primary`, `shadow-destructive`, etc.

**Motion:**

- Duration: `duration-fast` (120ms), `duration-base` (180ms), `duration-slow` (300ms), `duration-slower` (500ms)
- Easing: `ease-spring` (cubic-bezier(0.34, 1.56, 0.64, 1))

---

## Accessibility Checklist

✅ **Keyboard Navigation**

- All interactive elements are keyboard accessible
- Focus rings visible with 2px offset
- Logical tab order

✅ **ARIA Labels**

- Icon-only buttons have aria-label
- Form errors linked via aria-describedby
- Modals/alerts have proper roles

✅ **Color Contrast**

- All text meets WCAG AA (4.5:1 minimum)
- Focus rings have 3:1 contrast with background
- States indicated by more than color alone

✅ **Motion**

- Respects prefers-reduced-motion
- Animations are subtle and purposeful
- No autoplaying animations

✅ **Screen Readers**

- Semantic HTML (header, nav, main, aside, footer)
- Alt text for images
- Loading states announced
- Error states announced

---

## Migration Guide

### From Basic to Enhanced Components

**Before:**

```tsx
<button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
  Submit
</button>
```

**After:**

```tsx
<Button variant="primary">Submit</Button>
```

**Benefits:**

- Design tokens automatically applied
- All states handled (hover, active, focus, disabled)
- Consistent sizing and spacing
- Accessibility built-in
- Loading state available

### From Custom Forms to FormField

**Before:**

```tsx
<div>
  <label htmlFor="email">Email</label>
  <input id="email" type="email" />
  {error && <span style={{ color: "red" }}>{error}</span>}
</div>
```

**After:**

```tsx
<FormField error={!!error} errorMessage={error}>
  <FormLabel>Email</FormLabel>
  <FormInput type="email" />
  <FormError />
</FormField>
```

**Benefits:**

- Auto-generated IDs
- Proper ARIA linking
- Consistent error styling
- Less boilerplate

---

## Performance Tips

1. **Lazy Load Heavy Components**

   ```tsx
   const Dialog = dynamic(() => import("@/components/ui/dialog"));
   ```

2. **Use Skeleton States**

   - Show skeleton while data loads
   - Prevents layout shift

3. **Minimize Re-renders**

   - Use React.memo for complex components
   - Avoid inline functions in props

4. **Optimize Images**

   - Always use next/image
   - Proper sizes attribute
   - priority for above-fold

5. **Code Split Charts**
   ```tsx
   const LineChart = dynamic(() =>
     import("@/components/charts").then((m) => m.LineChart)
   );
   ```

---

## Testing Checklist

Before shipping:

- [ ] Test keyboard navigation (Tab, Enter, ESC, Arrows)
- [ ] Test with screen reader (NVDA/JAWS)
- [ ] Test 200% zoom (browser zoom to 200%)
- [ ] Test on mobile (375px width minimum)
- [ ] Test dark mode parity
- [ ] Test reduced motion (System Preferences)
- [ ] Verify focus rings visible
- [ ] Verify error states announced
- [ ] Verify loading states announced
- [ ] Run axe-core audit (0 critical/serious issues)

---

## Common Patterns

### Dashboard KPI Card

```tsx
<Card>
  <CardHeader>
    <CardTitle>Recovery Rate</CardTitle>
    <CardDescription>Last 30 days</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="flex items-baseline gap-space-2">
      <span className="text-4xl font-bold">65%</span>
      <Badge variant="success">↑ 12%</Badge>
    </div>
  </CardContent>
</Card>
```

### Form with Validation

```tsx
<form onSubmit={handleSubmit}>
  <FormField error={!!errors.email} errorMessage={errors.email}>
    <FormLabel required>Email</FormLabel>
    <FormInput
      type="email"
      placeholder="you@company.com"
      {...register("email")}
    />
    <FormError />
  </FormField>

  <FormField error={!!errors.password} errorMessage={errors.password}>
    <FormLabel required>Password</FormLabel>
    <FormInput type="password" {...register("password")} />
    <FormDescription>
      At least 8 characters with 1 uppercase, 1 number
    </FormDescription>
    <FormError />
  </FormField>

  <Button type="submit" loading={isSubmitting}>
    Create Account
  </Button>
</form>
```

### Confirmation Dialog

```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Delete Recovery Rule?</DialogTitle>
      <DialogDescription>
        This will permanently delete the rule "3 Retry Attempts". This action
        cannot be undone.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="secondary" onClick={() => setIsOpen(false)}>
        Cancel
      </Button>
      <Button variant="destructive" onClick={handleDelete} loading={isDeleting}>
        Delete Rule
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Data Table with States

```tsx
{
  isLoading ? (
    <SkeletonTable rows={10} />
  ) : error ? (
    <ErrorState
      title="Failed to load attempts"
      description={error.message}
      action={
        <Button variant="secondary" onClick={refetch}>
          Retry
        </Button>
      }
    />
  ) : data.length === 0 ? (
    <EmptyState
      icon={Inbox}
      title="No recovery attempts yet"
      description="Failed payments will appear here once integrated."
    />
  ) : (
    <DataTable data={data} columns={columns} />
  );
}
```

---

**Built with Stripe/Vercel-caliber quality • WCAG AA compliant • Performance optimized**
