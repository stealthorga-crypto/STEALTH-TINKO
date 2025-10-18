/**
 * Chart Components
 * 
 * Professional data visualization components using Recharts
 * - Zero-ink-waste principle (no chart junk)
 * - Accessible with ARIA labels
 * - Responsive by default
 * - Design token colors
 */

'use client'

import {
  LineChart as RechartsLineChart,
  BarChart as RechartsBarChart,
  PieChart as RechartsPieChart,
  Line,
  Bar,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { cn } from '@/lib/utils'

// ============================================================================
// CHART COLORS - Using design tokens
// ============================================================================

export const CHART_COLORS = {
  primary: 'hsl(var(--primary))',
  success: 'hsl(var(--success))',
  warning: 'hsl(var(--warning))',
  destructive: 'hsl(var(--destructive))',
  info: 'hsl(var(--info))',
  muted: 'hsl(var(--muted-foreground))',
}

const PIE_COLORS = [
  CHART_COLORS.primary,
  CHART_COLORS.success,
  CHART_COLORS.warning,
  CHART_COLORS.info,
  CHART_COLORS.muted,
]

// ============================================================================
// CUSTOM TOOLTIP - Accessible and styled
// ============================================================================

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    color?: string
    name?: string
    value?: number
  }>
  label?: string
  formatter?: (value: number) => string
}

function CustomTooltip({ active, payload, label, formatter }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div
      className="bg-card border border-border rounded-lg shadow-lg p-3"
      role="tooltip"
    >
      {label && (
        <p className="text-sm font-medium mb-2 text-foreground">{label}</p>
      )}
      {payload.map((entry, index: number) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <div
            className="h-3 w-3 rounded-sm"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-muted-foreground">{entry.name}:</span>
          <span className="font-medium text-foreground">
            {formatter && entry.value ? formatter(entry.value) : entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// ============================================================================
// LINE CHART - For trends over time
// ============================================================================

interface LineChartProps {
  data: Array<Record<string, string | number>>
  xKey: string
  yKey: string
  title?: string
  height?: number
  color?: keyof typeof CHART_COLORS
  formatter?: (value: number) => string
  className?: string
}

/**
 * Line chart for time-series data
 * 
 * @example
 * <LineChart
 *   data={revenueData}
 *   xKey="date"
 *   yKey="revenue"
 *   title="Revenue Trend"
 *   formatter={(value) => `$${value.toLocaleString()}`}
 * />
 */
export function LineChart({
  data,
  xKey,
  yKey,
  title,
  height = 300,
  color = 'primary',
  formatter,
  className,
}: LineChartProps) {
  return (
    <div className={cn('w-full', className)} role="figure" aria-label={title}>
      {title && (
        <h3 className="text-sm font-medium mb-4 text-foreground">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsLineChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
            opacity={0.5}
          />
          <XAxis
            dataKey={xKey}
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
            tickFormatter={formatter}
          />
          <Tooltip content={<CustomTooltip formatter={formatter} />} />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke={CHART_COLORS[color]}
            strokeWidth={2}
            dot={{ fill: CHART_COLORS[color], r: 4 }}
            activeDot={{ r: 6 }}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  )
}

// ============================================================================
// BAR CHART - For comparisons
// ============================================================================

interface BarChartProps {
  data: Array<Record<string, string | number>>
  xKey: string
  yKey: string
  title?: string
  height?: number
  color?: keyof typeof CHART_COLORS
  formatter?: (value: number) => string
  className?: string
}

/**
 * Bar chart for categorical comparisons
 * 
 * @example
 * <BarChart
 *   data={pspData}
 *   xKey="provider"
 *   yKey="failureRate"
 *   title="Failure Rate by PSP"
 *   formatter={(value) => `${value}%`}
 * />
 */
export function BarChart({
  data,
  xKey,
  yKey,
  title,
  height = 300,
  color = 'primary',
  formatter,
  className,
}: BarChartProps) {
  return (
    <div className={cn('w-full', className)} role="figure" aria-label={title}>
      {title && (
        <h3 className="text-sm font-medium mb-4 text-foreground">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
            opacity={0.5}
          />
          <XAxis
            dataKey={xKey}
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
            tickFormatter={formatter}
          />
          <Tooltip content={<CustomTooltip formatter={formatter} />} />
          <Bar
            dataKey={yKey}
            fill={CHART_COLORS[color]}
            radius={[6, 6, 0, 0]}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ============================================================================
// PIE CHART - For proportions
// ============================================================================

interface PieChartProps {
  data: Array<{ name: string; value: number }>
  title?: string
  height?: number
  formatter?: (value: number) => string
  className?: string
}

/**
 * Pie chart for showing proportions
 * 
 * @example
 * <PieChart
 *   data={[
 *     { name: 'Recovered', value: 65 },
 *     { name: 'Failed', value: 35 }
 *   ]}
 *   title="Recovery Success Rate"
 *   formatter={(value) => `${value}%`}
 * />
 */
export function PieChart({
  data,
  title,
  height = 300,
  formatter,
  className,
}: PieChartProps) {
  return (
    <div className={cn('w-full', className)} role="figure" aria-label={title}>
      {title && (
        <h3 className="text-sm font-medium mb-4 text-foreground">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(entry: { name?: string; percent?: number }) =>
              `${entry.name || ''} ${((entry.percent || 0) * 100).toFixed(0)}%`
            }
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={PIE_COLORS[index % PIE_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip formatter={formatter} />} />
          <Legend
            wrapperStyle={{
              paddingTop: '20px',
              fontSize: '12px',
            }}
          />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  )
}

// ============================================================================
// FUNNEL CHART - For conversion funnels
// ============================================================================

interface FunnelChartProps {
  data: Array<{ stage: string; count: number; percentage?: number }>
  title?: string
  className?: string
}

/**
 * Funnel chart for showing conversion steps
 * 
 * @example
 * <FunnelChart
 *   data={[
 *     { stage: 'Failed Payments', count: 1000 },
 *     { stage: 'Retry Attempts', count: 800 },
 *     { stage: 'Recovered', count: 650 }
 *   ]}
 *   title="Recovery Funnel"
 * />
 */
export function FunnelChart({ data, title, className }: FunnelChartProps) {
  const maxCount = Math.max(...data.map((d) => d.count))

  return (
    <div className={cn('w-full', className)} role="figure" aria-label={title}>
      {title && (
        <h3 className="text-sm font-medium mb-4 text-foreground">{title}</h3>
      )}
      <div className="space-y-3">
        {data.map((item, index) => {
          const widthPercent = (item.count / maxCount) * 100
          const displayPercent = item.percentage || Math.round(widthPercent)

          return (
            <div key={index} className="flex items-center gap-4">
              <div className="w-32 text-sm text-muted-foreground">
                {item.stage}
              </div>
              <div className="flex-1">
                <div className="relative h-12 rounded-lg overflow-hidden bg-muted">
                  <div
                    className="absolute inset-y-0 left-0 bg-primary flex items-center justify-end pr-4 transition-all duration-500"
                    style={{ width: `${widthPercent}%` }}
                  >
                    <span className="text-sm font-medium text-primary-foreground">
                      {item.count.toLocaleString()} ({displayPercent}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
