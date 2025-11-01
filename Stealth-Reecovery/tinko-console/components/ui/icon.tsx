/**
 * Icon Component
 * 
 * Consistent icon wrapper for lucide-react icons
 * - Standard sizing (20-24px for optimal legibility)
 * - Consistent stroke width
 * - Accessible with proper ARIA labels
 * - Design token colors
 */

import { type LucideIcon, type LucideProps } from 'lucide-react'
import { cn } from '@/lib/utils'

interface IconProps extends Omit<LucideProps, 'ref'> {
  /**
   * The lucide-react icon component to render
   */
  icon: LucideIcon
  
  /**
   * Icon size preset
   * @default 'base'
   */
  size?: 'sm' | 'base' | 'lg' | 'xl'
  
  /**
   * Accessible label for screen readers
   * Required for standalone icons (not next to text)
   */
  label?: string
  
  /**
   * Whether the icon is decorative (hidden from screen readers)
   * Set to true only if icon duplicates adjacent text
   * @default false
   */
  decorative?: boolean
}

const sizeMap = {
  sm: 16,
  base: 20,
  lg: 24,
  xl: 32,
}

/**
 * Icon wrapper component
 * 
 * @example
 * // Standalone icon (requires label)
 * <Icon icon={CheckCircle} label="Success" className="text-success" />
 * 
 * @example
 * // Decorative icon (next to text)
 * <button>
 *   <Icon icon={ArrowRight} decorative />
 *   Continue
 * </button>
 */
export function Icon({
  icon: LucideIcon,
  size = 'base',
  label,
  decorative = false,
  className,
  ...props
}: IconProps) {
  const sizeValue = sizeMap[size]
  
  // Accessibility check: standalone icons need labels
  if (!decorative && !label && process.env.NODE_ENV === 'development') {
    console.warn(
      'Icon: Standalone icons should have a `label` prop for accessibility. ' +
      'If the icon is purely decorative (duplicates adjacent text), set `decorative={true}`.'
    )
  }
  
  return (
    <LucideIcon
      size={sizeValue}
      strokeWidth={2}
      aria-label={!decorative ? label : undefined}
      aria-hidden={decorative}
      className={cn(
        'shrink-0', // Prevent icon from shrinking in flex layouts
        className
      )}
      {...props}
    />
  )
}

/**
 * Icon group for multiple icons
 * Ensures consistent spacing
 */
interface IconGroupProps {
  children: React.ReactNode
  className?: string
}

export function IconGroup({ children, className }: IconGroupProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-2',
        className
      )}
      role="group"
    >
      {children}
    </div>
  )
}

/**
 * Icon button wrapper
 * For icon-only buttons with proper accessibility
 */
interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon
  label: string // Required for a11y
  size?: 'sm' | 'base' | 'lg'
}

export function IconButton({
  icon,
  label,
  size = 'base',
  className,
  ...props
}: IconButtonProps) {
  return (
    <button
      aria-label={label}
      className={cn(
        'inline-flex items-center justify-center rounded-md',
        'transition-colors duration-fast',
        'hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        {
          'h-8 w-8': size === 'sm',
          'h-10 w-10': size === 'base',
          'h-12 w-12': size === 'lg',
        },
        className
      )}
      {...props}
    >
      <Icon icon={icon} size={size} decorative />
    </button>
  )
}
