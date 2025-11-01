import { type ReactNode } from "react"
import { AlertTriangle } from "lucide-react"
import { Icon } from "@/components/ui/icon"

interface ErrorStateProps {
  title?: string
  description?: string
  action?: ReactNode
}

export function ErrorState({
  title = "Something went wrong",
  description = "Please try again or contact support if the problem persists.",
  action,
}: ErrorStateProps) {
  return (
    <div className="flex items-start gap-space-4 rounded-xl border border-destructive/20 bg-destructive-light/50 dark:bg-destructive/5 p-space-6" role="alert">
      <div className="flex size-10 items-center justify-center rounded-full bg-destructive/10 text-destructive shrink-0">
        <Icon icon={AlertTriangle} size="base" decorative />
      </div>
      <div className="flex-1 space-y-space-2">
        <h3 className="text-lg font-semibold text-destructive tracking-tight">{title}</h3>
        <p className="text-sm text-muted-foreground leading-normal">{description}</p>
        {action && <div className="pt-space-2">{action}</div>}
      </div>
    </div>
  )
}
