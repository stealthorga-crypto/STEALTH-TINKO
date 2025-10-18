import { type ReactNode } from "react"
import { Icon } from "@/components/ui/icon"
import { LucideIcon } from "lucide-react"

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description: string
  action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-space-4 rounded-xl border-2 border-dashed border-border/70 bg-muted/20 p-space-12 text-center">
      {icon && (
        <div className="rounded-full bg-muted p-space-4">
          <Icon icon={icon} size="xl" className="text-muted-foreground" decorative />
        </div>
      )}
      <div className="space-y-space-2">
        <h3 className="text-lg font-semibold text-foreground tracking-tight">{title}</h3>
        <p className="max-w-md text-sm text-muted-foreground leading-normal">{description}</p>
      </div>
      {action && <div className="flex items-center gap-space-2 mt-space-2">{action}</div>}
    </div>
  )
}
