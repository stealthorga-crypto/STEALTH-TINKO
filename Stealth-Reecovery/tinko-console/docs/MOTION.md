# Motion & Micro-interactions

**Version**: 2.0.0  
**Phase**: 2 of Design System Overhaul  
**Quality Bar**: Delightful, Professional, Accessible

---

## Philosophy

Motion is **never decorative** — it should:

1. **Provide Feedback**: Confirm user actions (button press, card selection)
2. **Guide Attention**: Draw focus to important changes (toasts, modals)
3. **Enhance Perception**: Make interactions feel responsive and alive
4. **Respect Users**: Always honor `prefers-reduced-motion`

**Golden Rule**: If removing an animation breaks the experience, it's necessary. If not, question whether you need it.

---

## Design Principles

### 1. Speed & Timing

- **Fast (120ms)**: Hover, focus, button press — instant feedback
- **Base (180ms)**: Default transitions — smooth but not sluggish
- **Slow (300ms)**: Panel slides, drawer open/close — deliberate movement
- **Slower (500ms)**: Page transitions, major state changes — allow comprehension

**Never exceed 500ms** — users perceive delays beyond this as unresponsive.

### 2. Easing Curves

| Curve         | Bezier                              | Usage                           |
| ------------- | ----------------------------------- | ------------------------------- |
| `ease-in`     | `cubic-bezier(0.4, 0, 1, 1)`        | Elements leaving the screen     |
| `ease-out`    | `cubic-bezier(0, 0, 0.2, 1)`        | Elements entering the screen    |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)`      | Default (smooth both ends)      |
| `ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful bounce (use sparingly!) |

**Default to ease-in-out** unless you have a specific reason.

### 3. Distance & Scale

- **Hover lift**: 2-4px vertical translation (cards, buttons)
- **Button press**: 2-3% scale down (0.97-0.98)
- **Modal/popover**: Scale from 95% to 100%
- **Slide distances**: Keep under 100% viewport width/height

---

## Motion Components

### FadeIn

**When to use**: Page loads, content reveals, gentle transitions

```tsx
import { MotionWrapper } from "@/components/ui/motion";

<MotionWrapper variant="fadeIn">
  <Card>Content fades in smoothly</Card>
</MotionWrapper>;
```

**Timing**: 180ms ease-out  
**Use case**: New content appearing, initial page load

---

### SlideUp

**When to use**: Toasts, modals, bottom sheets

```tsx
<MotionWrapper variant="slideUp">
  <div className="bg-card rounded-lg p-6">Slides up from bottom</div>
</MotionWrapper>
```

**Timing**: 180ms spring easing  
**Use case**: Notifications, drawer panels, success messages

---

### SlideDown

**When to use**: Dropdowns, accordions, top banners

```tsx
<MotionWrapper variant="slideDown">
  <DropdownMenu>Slides down from top</DropdownMenu>
</MotionWrapper>
```

**Timing**: 180ms spring easing  
**Use case**: Navigation menus, expanding panels

---

### ScaleIn

**When to use**: Modals, popovers, tooltips

```tsx
<MotionWrapper variant="scaleIn">
  <Dialog>Scales in from 95% to 100%</Dialog>
</MotionWrapper>
```

**Timing**: 120ms spring easing  
**Use case**: Overlays, confirmations, popups

---

### StaggerChildren

**When to use**: Lists, grids, sequential reveals

```tsx
<MotionWrapper variant="stagger">
  {items.map((item) => (
    <MotionWrapper key={item.id} variant="fadeIn">
      <Card>{item.content}</Card>
    </MotionWrapper>
  ))}
</MotionWrapper>
```

**Timing**: 60ms stagger delay per child  
**Use case**: Card grids, list items, feature sections

---

## Interactive Components

### AnimatedButton

Tactile press animation with scale feedback:

```tsx
import { AnimatedButton } from "@/components/ui/motion";

<AnimatedButton onClick={handleClick} className="btn-primary">
  Start Free Trial
</AnimatedButton>;
```

**Interaction**:

- Hover: Scale to 102%
- Press: Scale to 97%
- Release: Spring back to 100%

**Timing**: 120ms spring easing  
**Accessibility**: Respects reduced motion (no animation)

---

### AnimatedCard

Subtle lift on hover for interactive cards:

```tsx
import { AnimatedCard } from "@/components/ui/motion";

<AnimatedCard className="card-surface p-6">
  <h3>Recovery Success</h3>
  <p>Card lifts on hover</p>
</AnimatedCard>;
```

**Interaction**:

- Hover: Translate -4px (lift), shadow increases
- Default: Returns to baseline

**Timing**: 180ms ease-out  
**Use case**: Clickable cards, feature tiles, navigation items

---

## Layout Transitions

### PageTransition

Smooth transitions between route changes:

```tsx
import { PageTransition } from "@/components/ui/motion";

export default function Page() {
  return (
    <PageTransition>
      <main>Page content with fade + subtle slide</main>
    </PageTransition>
  );
}
```

**Timing**: 180ms ease-in-out  
**Behavior**: Fade in + 8px upward slide

---

## Specialized Variants

### Toast Animations

Pre-configured for notification toasts:

```tsx
import { motion } from "framer-motion";
import { toastVariants } from "@/components/ui/motion";

<motion.div
  variants={toastVariants}
  initial="initial"
  animate="animate"
  exit="exit"
  className="bg-card shadow-lg rounded-lg p-4"
>
  Payment recovered successfully!
</motion.div>;
```

**Behavior**: Slide in from right + scale + fade  
**Timing**: 180ms spring easing  
**Exit**: Slide out right (120ms)

---

### Sidebar/Drawer Animations

Slide-in from left for navigation:

```tsx
import { motion } from "framer-motion";
import { sidebarVariants } from "@/components/ui/motion";

<motion.aside
  variants={sidebarVariants}
  initial="closed"
  animate={isOpen ? "open" : "closed"}
  className="fixed left-0 top-0 h-full w-64 bg-card"
>
  Sidebar content
</motion.aside>;
```

**Timing**: 180ms ease-in-out  
**Behavior**: Slide from left edge

---

### Backdrop/Overlay

Fade background for modals:

```tsx
import { motion } from "framer-motion";
import { backdropVariants } from "@/components/ui/motion";

<motion.div
  variants={backdropVariants}
  initial="hidden"
  animate="visible"
  exit="hidden"
  className="fixed inset-0 bg-black/50"
  onClick={handleClose}
/>;
```

**Timing**: 120ms fade  
**Behavior**: Black overlay with 50% opacity

---

## Accessibility

### Reduced Motion

**CRITICAL**: All animations respect `prefers-reduced-motion: reduce`.

The motion components automatically disable animations when users have this preference enabled:

```tsx
import { usePrefersReducedMotion } from "@/components/ui/motion";

function Component() {
  const prefersReduced = usePrefersReducedMotion();

  if (prefersReduced) {
    return <StaticContent />; // No animations
  }

  return <AnimatedContent />; // With animations
}
```

**CSS Fallback** (already in globals.css):

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Never override this behavior** — it's an accessibility requirement.

---

## Common Patterns

### Button with Press Feedback

```tsx
<AnimatedButton onClick={handleSubmit} className="btn-primary">
  Submit Form
</AnimatedButton>
```

### Hover Card Grid

```tsx
<div className="grid grid-cols-3 gap-6">
  {features.map((feature) => (
    <AnimatedCard
      key={feature.id}
      className="card-surface p-6 cursor-pointer"
      onClick={() => handleSelect(feature)}
    >
      <h3>{feature.title}</h3>
      <p>{feature.description}</p>
    </AnimatedCard>
  ))}
</div>
```

### Toast Notification

```tsx
import { Toaster } from "sonner";

// Already configured with motion
<Toaster
  position="top-right"
  toastOptions={{
    className: "animate-slide-up",
    duration: 4000,
  }}
/>;
```

### Modal Dialog

```tsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        variants={backdropVariants}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="fixed inset-0 bg-black/50"
      />

      <MotionWrapper variant="scaleIn">
        <Dialog>
          <DialogTitle>Confirm Action</DialogTitle>
          <DialogContent>Are you sure?</DialogContent>
          <DialogActions>
            <AnimatedButton onClick={handleConfirm}>Confirm</AnimatedButton>
          </DialogActions>
        </Dialog>
      </MotionWrapper>
    </>
  )}
</AnimatePresence>
```

### Page Load Stagger

```tsx
<MotionWrapper variant="stagger">
  <MotionWrapper variant="fadeIn">
    <PageHeader />
  </MotionWrapper>

  <MotionWrapper variant="fadeIn">
    <KpiCards />
  </MotionWrapper>

  <MotionWrapper variant="fadeIn">
    <DataTable />
  </MotionWrapper>
</MotionWrapper>
```

---

## Performance Tips

### 1. Use CSS Transforms

Always animate `transform` and `opacity` — these are GPU-accelerated:

```tsx
// ✅ Good: GPU-accelerated
<motion.div
  animate={{ x: 100, opacity: 0.5 }}
/>

// ❌ Bad: Forces layout recalculation
<motion.div
  animate={{ left: '100px', opacity: 0.5 }}
/>
```

### 2. Avoid Layout Thrashing

Don't animate `width`, `height`, `top`, `left` — use `scale` and `translate` instead:

```tsx
// ✅ Good
<motion.div
  animate={{ scale: 1.5 }}
/>

// ❌ Bad
<motion.div
  animate={{ width: '150%' }}
/>
```

### 3. Use `AnimatePresence` for Exit Animations

Required for elements that unmount:

```tsx
import { AnimatePresence } from "framer-motion";

<AnimatePresence>
  {isVisible && (
    <MotionWrapper variant="fadeIn">
      <Component />
    </MotionWrapper>
  )}
</AnimatePresence>;
```

### 4. Debounce Frequent Animations

For scroll-triggered animations, use `IntersectionObserver`:

```tsx
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

function ScrollReveal() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
    >
      Reveals when scrolled into view
    </motion.div>
  );
}
```

---

## Do's and Don'ts

### ✅ Do

- Use motion to provide feedback on user actions
- Keep animations under 500ms
- Respect `prefers-reduced-motion`
- Animate `transform` and `opacity` for performance
- Test on mid-range devices (not just high-end)
- Use spring easing sparingly for delight

### ❌ Don't

- Add motion just because you can
- Animate layout properties (`width`, `height`, `top`, `left`)
- Ignore reduced motion preferences
- Use animations longer than 500ms
- Apply spring easing to every interaction
- Animate on every hover (causes distraction)

---

## Testing Checklist

Before shipping animations:

- [ ] Test on mobile (mid-range Android)
- [ ] Verify `prefers-reduced-motion` disables animations
- [ ] Check 60fps in Chrome DevTools Performance tab
- [ ] Test keyboard navigation (focus states)
- [ ] Verify no layout shift during animations
- [ ] Ensure smooth exit animations
- [ ] Test with slow 3G network throttling

---

## Resources

- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Web Animation Principles](https://web.dev/animations/)
- [Reduced Motion](https://web.dev/prefers-reduced-motion/)
- [Performance Budgets](https://web.dev/performance-budgets-101/)

---

## Future Enhancements (Phase 9)

- Hero recovery flow line animation (SVG path drawing)
- Data chart enter animations (stagger bars/lines)
- Confetti on successful recovery (celebrate wins)
- Loading skeleton transitions (smooth content replacement)
