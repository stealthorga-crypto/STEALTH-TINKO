import * as React from "react"
import { AlertCircle, CheckCircle2, Info, XCircle } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const bannerVariants = cva(
  "flex items-start gap-space-3 rounded-lg px-space-4 py-space-3 border",
  {
    variants: {
      variant: {
        info: "bg-info-light border-info/20 text-info dark:bg-info/10",
        success: "bg-success-light border-success/20 text-success dark:bg-success/10",
        warning: "bg-warning-light border-warning/20 text-warning dark:bg-warning/10",
        destructive: "bg-destructive-light border-destructive/20 text-destructive dark:bg-destructive/10",
      },
    },
    defaultVariants: {
      variant: "info",
    },
  }
)

const icons = {
  info: Info,
  success: CheckCircle2,
  warning: AlertCircle,
  destructive: XCircle,
}

interface BannerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof bannerVariants> {
  onDismiss?: () => void
}

function Banner({ variant = "info", className, children, onDismiss, ...props }: BannerProps) {
  const Icon = icons[variant || "info"]

  return (
    <div className={cn(bannerVariants({ variant }), className)} role="alert" {...props}>
      <Icon className="size-5 shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex-1 text-sm leading-normal">{children}</div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded-md hover:bg-black/5 dark:hover:bg-white/5 p-1 transition-colors"
          aria-label="Dismiss"
        >
          <XCircle className="size-4" />
        </button>
      )}
    </div>
  )
}

function InlineAlert({ variant = "info", className, children, ...props }: BannerProps) {
  const Icon = icons[variant || "info"]

  return (
    <div
      className={cn(
        "flex items-start gap-space-2 text-sm",
        variant === "info" && "text-info",
        variant === "success" && "text-success",
        variant === "warning" && "text-warning",
        variant === "destructive" && "text-destructive",
        className
      )}
      role="alert"
      {...props}
    >
      <Icon className="size-4 shrink-0 mt-0.5" aria-hidden="true" />
      <div className="leading-normal">{children}</div>
    </div>
  )
}

export { Banner, InlineAlert }
