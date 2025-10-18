import * as React from "react"

import { cn } from "@/lib/utils"

export type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  error?: boolean
  success?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, success, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border bg-card px-space-4 py-space-2 text-sm shadow-xs transition-all duration-base ease-spring",
          "placeholder:text-muted-foreground",
          "focus:outline-none focus:outline-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted",
          "dark:bg-card dark:text-foreground",
          // Default state
          !error && !success && "border-input focus:border-primary focus:ring-2 focus:ring-primary/20",
          // Error state
          error && "border-destructive focus:border-destructive focus:ring-2 focus:ring-destructive/20 aria-invalid:border-destructive",
          // Success state
          success && "border-success focus:border-success focus:ring-2 focus:ring-success/20",
          className
        )}
        aria-invalid={error}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
