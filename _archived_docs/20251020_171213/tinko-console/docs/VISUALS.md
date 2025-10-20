# Iconography & Data Visualization

**Version**: 2.0.0  
**Phase**: 3 of Design System Overhaul  
**Principle**: Zero-Ink-Waste — Every pixel serves a purpose

---

## Philosophy

Data visualization should:

1. **Prioritize Clarity**: Remove chart junk, maximize data-ink ratio
2. **Guide Understanding**: Use color and hierarchy to emphasize key insights
3. **Respect Accessibility**: Provide text alternatives, ARIA labels, keyboard navigation
4. **Maintain Consistency**: Use design tokens for colors, sizing, spacing

**Edward Tufte's Data-Ink Ratio**: Maximize the proportion of ink used to display actual data vs. decorative elements.

---

## Icon System

### Icon Component

Standard wrapper for lucide-react icons with consistent sizing and accessibility:

```tsx
import { Icon } from '@/components/ui/icon'
import { CheckCircle, AlertTriangle } from 'lucide-react'

// Standalone icon (requires label)
<Icon icon={CheckCircle} label="Success" className="text-success" />

// Decorative icon (next to text)
<button>
  <Icon icon={AlertTriangle} decorative />
  Warning: Payment failed
</button>
```

### Icon Sizing

| Size   | Pixels | Usage                         |
| ------ | ------ | ----------------------------- |
| `sm`   | 16px   | Inline with text, compact UIs |
| `base` | 20px   | Default, buttons, navigation  |
| `lg`   | 24px   | Feature tiles, headers        |
| `xl`   | 32px   | Hero sections, large CTAs     |

**Stroke width**: Always 2px for consistency (lucide-react default)

---

### Icon Accessibility

**✅ Do**:

```tsx
// Icon with text (decorative)
<button>
  <Icon icon={Save} decorative />
  Save Changes
</button>

// Standalone icon (needs label)
<Icon icon={Settings} label="Open settings" />

// Icon button (requires label)
<IconButton icon={X} label="Close dialog" onClick={handleClose} />
```

**❌ Don't**:

```tsx
// Missing label on standalone icon
<Icon icon={Settings} />

// Missing label on icon-only button
<button><CheckIcon /></button>
```

---

### Icon Variants

#### Success Icons

- `CheckCircle` — Confirmation, completed actions
- `CheckSquare` — Checkbox states, task completion
- `ThumbsUp` — Approval, positive feedback

#### Warning Icons

- `AlertTriangle` — Warnings, cautionary messages
- `AlertCircle` — Information alerts
- `Clock` — Time-sensitive warnings

#### Error Icons

- `XCircle` — Errors, failed actions
- `AlertOctagon` — Critical errors
- `Ban` — Blocked, forbidden actions

#### Navigation Icons

- `ArrowRight` — Forward navigation, "next"
- `ArrowLeft` — Back navigation, "previous"
- `ChevronDown` — Dropdown indicators
- `Menu` — Mobile menu toggle

#### Data Icons

- `TrendingUp` — Positive trends, growth
- `TrendingDown` — Negative trends, decline
- `BarChart3` — Analytics, reports
- `PieChart` — Proportions, distributions

---

## Figure Component

Semantic wrapper for visual content with captions:

```tsx
import { Figure } from "@/components/ui/figure";

<Figure caption="Revenue trend over last 30 days">
  <LineChart data={revenueData} xKey="date" yKey="revenue" />
</Figure>;
```

### Accessibility Features

- Uses semantic `<figure>` and `<figcaption>` HTML elements
- Provides `role="img"` for screen readers
- Links caption to figure via `aria-labelledby`
- Warns in development if missing accessibility props

---

## Icon Tiles

Colored backgrounds for feature sections:

```tsx
import { IconTile } from "@/components/ui/figure";
import { Zap } from "lucide-react";

<IconTile icon={<Zap size={24} />} variant="success" size="lg" />;
```

**Variants**:

- `primary` — Primary brand actions
- `success` — Positive outcomes
- `warning` — Cautionary features
- `info` — Informational content
- `muted` — Secondary features

---

## Chart Components

### LineChart

**Usage**: Time-series data, trends over time

```tsx
import { LineChart } from "@/components/charts";

<LineChart
  data={[
    { date: "Jan", revenue: 12000 },
    { date: "Feb", revenue: 15000 },
    { date: "Mar", revenue: 18000 },
  ]}
  xKey="date"
  yKey="revenue"
  title="Revenue Trend"
  formatter={(value) => `$${value.toLocaleString()}`}
  color="primary"
  height={300}
/>;
```

**Features**:

- Monotone curved line for smooth appearance
- Active dot enlarges on hover
- Responsive container (100% width)
- Custom tooltip with formatted values
- Design token colors

---

### BarChart

**Usage**: Categorical comparisons, rankings

```tsx
import { BarChart } from "@/components/charts";

<BarChart
  data={[
    { provider: "Stripe", failureRate: 2.5 },
    { provider: "PayPal", failureRate: 3.8 },
    { provider: "Square", failureRate: 4.2 },
  ]}
  xKey="provider"
  yKey="failureRate"
  title="Failure Rate by PSP"
  formatter={(value) => `${value}%`}
  color="destructive"
/>;
```

**Features**:

- Rounded top corners (6px radius)
- Minimal grid lines (low opacity)
- Sorted by value for clarity
- No border on bars (cleaner appearance)

---

### PieChart

**Usage**: Proportions, percentages, parts of a whole

```tsx
import { PieChart } from "@/components/charts";

<PieChart
  data={[
    { name: "Recovered", value: 65 },
    { name: "Failed", value: 35 },
  ]}
  title="Recovery Success Rate"
  formatter={(value) => `${value}%`}
  height={300}
/>;
```

**Features**:

- Automatic label positioning
- Legend below chart
- Color palette from design tokens
- Percentage labels on each slice

**When to use**:

- ✅ 2-5 categories (readable labels)
- ✅ Showing parts of a whole (must sum to 100%)
- ❌ Avoid for precise comparisons (use bar chart)
- ❌ Avoid for >5 categories (too cluttered)

---

### FunnelChart

**Usage**: Conversion funnels, sequential steps

```tsx
import { FunnelChart } from "@/components/charts";

<FunnelChart
  data={[
    { stage: "Failed Payments", count: 1000 },
    { stage: "Retry Attempts", count: 800 },
    { stage: "Recovered", count: 650 },
  ]}
  title="Recovery Funnel"
/>;
```

**Features**:

- Horizontal bars with proportional widths
- Automatic percentage calculation
- Drop-off visible at each stage
- Smooth width transitions (500ms)

---

## Chart Color Guidelines

### Single-Series Charts

Use semantic colors based on data meaning:

```tsx
// Positive metrics (revenue, growth, recovery)
<LineChart color="success" />

// Neutral metrics (volume, count, activity)
<LineChart color="primary" />

// Negative metrics (failures, errors, churn)
<LineChart color="destructive" />

// Informational metrics (requests, events)
<LineChart color="info" />
```

### Multi-Series Charts

Use distinct colors from design tokens:

```tsx
const CHART_COLORS = {
  primary: "hsl(var(--primary))",
  success: "hsl(var(--success))",
  warning: "hsl(var(--warning))",
  destructive: "hsl(var(--destructive))",
  info: "hsl(var(--info))",
};
```

**Color accessibility**: Ensure 3:1 contrast ratio between adjacent colors.

---

## Chart Accessibility

### ARIA Labels

All charts have `role="figure"` and `aria-label`:

```tsx
<LineChart
  title="Revenue Trend" // Becomes aria-label
  data={data}
  xKey="date"
  yKey="revenue"
/>
```

### Keyboard Navigation

Charts support keyboard interaction:

- **Tab**: Focus chart
- **Arrow keys**: Navigate data points
- **Enter/Space**: Activate tooltip

### Screen Reader Support

Provide data table alternative:

```tsx
<div className="sr-only">
  <table>
    <caption>Revenue trend data</caption>
    <thead>
      <tr>
        <th>Date</th>
        <th>Revenue</th>
      </tr>
    </thead>
    <tbody>
      {data.map(row => (
        <tr key={row.date}>
          <td>{row.date}</td>
          <td>${row.revenue.toLocaleString()}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>

<LineChart data={data} xKey="date" yKey="revenue" aria-hidden="true" />
```

---

## Zero-Ink-Waste Checklist

Before shipping a chart, verify:

- [ ] **No 3D effects** (distort data perception)
- [ ] **Minimal grid lines** (low opacity, necessary only)
- [ ] **No background colors** (unless essential for grouping)
- [ ] **Direct labels** (not relying solely on legend)
- [ ] **Sorted data** (where order matters)
- [ ] **Appropriate chart type** (bar > pie for comparisons)
- [ ] **Consistent scale** (zero-based for bar charts)
- [ ] **Accessible colors** (not relying on color alone)

---

## Common Patterns

### KPI Card with Trend

```tsx
<div className="card-surface p-6">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-sm font-medium text-muted-foreground">Recovery Rate</h3>
    <IconTile icon={<TrendingUp size={20} />} variant="success" size="sm" />
  </div>

  <div className="text-3xl font-semibold mb-2">65.3%</div>

  <div className="text-sm text-success">
    <Icon icon={ArrowUp} size="sm" decorative />
    +5.2% from last month
  </div>
</div>
```

### Dashboard Chart Grid

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div className="card-surface p-6">
    <LineChart
      data={revenueData}
      xKey="date"
      yKey="revenue"
      title="Revenue Trend"
      formatter={(v) => `$${v.toLocaleString()}`}
    />
  </div>

  <div className="card-surface p-6">
    <BarChart
      data={pspData}
      xKey="provider"
      yKey="failureRate"
      title="Failure Rate by PSP"
      formatter={(v) => `${v}%`}
    />
  </div>
</div>
```

### Report Section with Figure

```tsx
<section className="space-y-6">
  <div>
    <h2 className="text-2xl font-semibold mb-2">Recovery Performance</h2>
    <p className="text-muted-foreground">
      Analysis of payment recovery trends over the last quarter.
    </p>
  </div>

  <Figure caption="Quarterly recovery success rate showing steady improvement">
    <LineChart
      data={quarterlyData}
      xKey="month"
      yKey="recoveryRate"
      color="success"
      height={400}
    />
  </Figure>

  <p className="text-sm text-muted-foreground">
    The recovery rate improved by 12% in Q1 2024, driven by optimized retry
    logic and better payment method diversification.
  </p>
</section>
```

---

## Performance Considerations

### Lazy Loading

Charts are heavy — lazy load them:

```tsx
import dynamic from "next/dynamic";

const LineChart = dynamic(
  () =>
    import("@/components/charts").then((mod) => ({ default: mod.LineChart })),
  { ssr: false }
);
```

### Data Sampling

For large datasets (>100 points), sample data:

```tsx
function sampleData<T>(data: T[], maxPoints: number): T[] {
  if (data.length <= maxPoints) return data;

  const step = Math.ceil(data.length / maxPoints);
  return data.filter((_, i) => i % step === 0);
}

<LineChart data={sampleData(largeDataset, 50)} />;
```

### Responsive Containers

Always use `ResponsiveContainer` from Recharts:

```tsx
<ResponsiveContainer width="100%" height={300}>
  <RechartsLineChart>...</RechartsLineChart>
</ResponsiveContainer>
```

---

## Resources

- [lucide-react Icons](https://lucide.dev/icons/)
- [Recharts Documentation](https://recharts.org/)
- [Edward Tufte - Data-Ink Ratio](https://en.wikipedia.org/wiki/Data-ink_ratio)
- [ARIA Authoring Practices - Charts](https://www.w3.org/WAI/ARIA/apg/patterns/charts/)

---

## Future Enhancements (Phase 7)

- Sparkline component for inline trends
- Heatmap for time-based patterns
- Animated chart transitions
- Export chart as PNG/SVG
- Real-time streaming data support
