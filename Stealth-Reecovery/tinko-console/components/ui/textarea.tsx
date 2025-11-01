import * as React from "react"

import { cn } from "@/lib/utils"

export type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  error?: boolean
  success?: boolean
  autoResize?: boolean
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, success, autoResize, onChange, ...props }, ref) => {
    const textareaRef = React.useRef<HTMLTextAreaElement | null>(null)

    const resizeTextarea = React.useCallback(() => {
      const textarea = textareaRef.current
      if (textarea && autoResize) {
        textarea.style.height = "auto"
        textarea.style.height = `${textarea.scrollHeight}px`
      }
    }, [autoResize])

    React.useEffect(() => {
      if (autoResize) {
        resizeTextarea()
      }
    }, [autoResize, resizeTextarea])

    const handleChange = React.useCallback(
      (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        if (autoResize) {
          resizeTextarea()
        }
        onChange?.(e)
      },
      [autoResize, onChange, resizeTextarea]
    )

    return (
      <textarea
        className={cn(
          "flex min-h-[80px] w-full rounded-lg border bg-card px-space-4 py-space-3 text-sm shadow-xs transition-all duration-base ease-spring resize-y",
          "placeholder:text-muted-foreground",
          "focus:outline-none focus:outline-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted disabled:resize-none",
          "dark:bg-card dark:text-foreground",
          // Default state
          !error && !success && "border-input focus:border-primary focus:ring-2 focus:ring-primary/20",
          // Error state
          error && "border-destructive focus:border-destructive focus:ring-2 focus:ring-destructive/20 aria-invalid:border-destructive",
          // Success state
          success && "border-success focus:border-success focus:ring-2 focus:ring-success/20",
          // Auto-resize
          autoResize && "resize-none overflow-hidden",
          className
        )}
        aria-invalid={error}
        ref={(node) => {
          textareaRef.current = node
          if (typeof ref === "function") {
            ref(node)
          } else if (ref) {
            ref.current = node
          }
        }}
        onChange={handleChange}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
