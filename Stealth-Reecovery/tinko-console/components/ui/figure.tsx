/**
 * Figure Component
 * 
 * Semantic wrapper for visual content (illustrations, charts, diagrams)
 * with proper accessibility and caption support.
 */

import { cn } from '@/lib/utils'
import { type ReactNode } from 'react'

interface FigureProps {
  /**
   * Visual content (SVG, chart, illustration)
   */
  children: ReactNode
  
  /**
   * Caption text for the figure
   * Displayed below the visual content
   */
  caption?: string
  
  /**
   * Additional description for screen readers
   * Use when caption alone doesn't fully describe the content
   */
  'aria-describedby'?: string
  
  /**
   * Accessible label for the figure
   * Required if no caption is provided
   */
  'aria-label'?: string
  
  /**
   * Size variant
   * @default 'base'
   */
  size?: 'sm' | 'base' | 'lg' | 'full'
  
  /**
   * Aspect ratio (CSS aspect-ratio property)
   * @example '16/9', '4/3', '1/1'
   */
  aspectRatio?: string
  
  className?: string
}

/**
 * Figure component for visual content
 * 
 * @example
 * <Figure caption="Revenue trend over time">
 *   <LineChart data={revenueData} />
 * </Figure>
 * 
 * @example
 * <Figure 
 *   aria-label="Recovery success illustration"
 *   size="lg"
 *   aspectRatio="16/9"
 * >
 *   <svg>...</svg>
 * </Figure>
 */
export function Figure({
  children,
  caption,
  'aria-describedby': ariaDescribedBy,
  'aria-label': ariaLabel,
  size = 'base',
  aspectRatio,
  className,
}: FigureProps) {
  // Accessibility warning in development
  if (!caption && !ariaLabel && process.env.NODE_ENV === 'development') {
    console.warn(
      'Figure: Visual content should have either a `caption` or `aria-label` prop for accessibility.'
    )
  }
  
  const figureId = caption ? `figure-${Math.random().toString(36).substr(2, 9)}` : undefined
  
  return (
    <figure
      aria-label={!caption ? ariaLabel : undefined}
      aria-describedby={ariaDescribedBy}
      className={cn(
        'flex flex-col',
        {
          'gap-2': size === 'sm',
          'gap-3': size === 'base',
          'gap-4': size === 'lg' || size === 'full',
        },
        className
      )}
    >
      <div
        className={cn(
          'relative overflow-hidden rounded-lg',
          {
            'w-64': size === 'sm',
            'w-96': size === 'base',
            'w-full max-w-2xl': size === 'lg',
            'w-full': size === 'full',
          }
        )}
        style={aspectRatio ? { aspectRatio } : undefined}
        role="img"
        aria-labelledby={figureId}
      >
        {children}
      </div>
      
      {caption && (
        <figcaption
          id={figureId}
          className={cn(
            'text-sm text-muted-foreground',
            {
              'text-xs': size === 'sm',
              'text-sm': size === 'base' || size === 'lg',
              'text-base': size === 'full',
            }
          )}
        >
          {caption}
        </figcaption>
      )}
    </figure>
  )
}

/**
 * Illustration wrapper for geometric SVG illustrations
 * Optimized for minimal, professional graphics
 */
interface IllustrationProps {
  /**
   * SVG children
   */
  children: ReactNode
  
  /**
   * Accessible title for the illustration
   */
  title: string
  
  /**
   * Illustration size
   * @default 'base'
   */
  size?: 'sm' | 'base' | 'lg' | 'xl'
  
  /**
   * Color scheme
   * @default 'primary'
   */
  variant?: 'primary' | 'success' | 'warning' | 'muted'
  
  className?: string
}

const illustrationSizes = {
  sm: 'h-24 w-24',
  base: 'h-32 w-32',
  lg: 'h-48 w-48',
  xl: 'h-64 w-64',
}

const illustrationColors = {
  primary: 'text-primary',
  success: 'text-success',
  warning: 'text-warning',
  muted: 'text-muted-foreground',
}

/**
 * Illustration component for SVG graphics
 * 
 * @example
 * <Illustration title="Payment recovery" size="lg" variant="success">
 *   <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 *     <circle cx="100" cy="100" r="80" fill="currentColor" opacity="0.2" />
 *     <path d="M60,100 L90,130 L140,70" stroke="currentColor" strokeWidth="8" fill="none" />
 *   </svg>
 * </Illustration>
 */
export function Illustration({
  children,
  title,
  size = 'base',
  variant = 'primary',
  className,
}: IllustrationProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center justify-center',
        illustrationSizes[size],
        illustrationColors[variant],
        className
      )}
      role="img"
      aria-label={title}
    >
      {children}
    </div>
  )
}

/**
 * Icon tile for feature sections
 * Combines icon with colored background
 */
interface IconTileProps {
  /**
   * Icon component (from lucide-react)
   */
  icon: React.ReactNode
  
  /**
   * Color variant
   * @default 'primary'
   */
  variant?: 'primary' | 'success' | 'warning' | 'info' | 'muted'
  
  /**
   * Size preset
   * @default 'base'
   */
  size?: 'sm' | 'base' | 'lg'
  
  className?: string
}

const tileVariants = {
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success-light text-success',
  warning: 'bg-warning-light text-warning',
  info: 'bg-info-light text-info',
  muted: 'bg-muted text-muted-foreground',
}

const tileSizes = {
  sm: 'h-10 w-10',
  base: 'h-12 w-12',
  lg: 'h-16 w-16',
}

/**
 * Icon tile component for feature sections
 * 
 * @example
 * <IconTile icon={<CheckCircle size={24} />} variant="success" />
 */
export function IconTile({
  icon,
  variant = 'primary',
  size = 'base',
  className,
}: IconTileProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center justify-center rounded-xl',
        tileVariants[variant],
        tileSizes[size],
        className
      )}
      aria-hidden="true" // Decorative, relies on adjacent text
    >
      {icon}
    </div>
  )
}
