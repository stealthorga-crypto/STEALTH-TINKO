import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-space-1 rounded-full text-xs font-medium transition-all duration-base ease-spring select-none",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        success: "bg-success-light text-success dark:bg-success/20 dark:text-success",
        warning: "bg-warning-light text-warning dark:bg-warning/20 dark:text-warning",
        destructive: "bg-destructive-light text-destructive dark:bg-destructive/20 dark:text-destructive",
        info: "bg-info-light text-info dark:bg-info/20 dark:text-info",
        secondary: "bg-secondary text-secondary-foreground",
        outline: "text-foreground border border-border bg-background",
      },
      size: {
        sm: "px-space-2 py-space-0.5 text-xs",
        default: "px-space-3 py-space-1 text-xs",
        lg: "px-space-4 py-space-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  removable?: boolean
  onRemove?: () => void
}

function Badge({ className, variant, size, removable, onRemove, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {children}
      {removable && onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-space-1 rounded-full hover:bg-black/10 dark:hover:bg-white/10 p-0.5 transition-colors"
          aria-label="Remove"
        >
          <X className="size-3" />
        </button>
      )}
    </div>
  )
}

export { Badge, badgeVariants }
