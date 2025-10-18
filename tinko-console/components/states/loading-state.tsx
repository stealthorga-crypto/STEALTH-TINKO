import { Skeleton, SkeletonText } from "@/components/ui/skeleton"

interface LoadingStateProps {
  label?: string
}

export function LoadingState({ label = "Loading data" }: LoadingStateProps) {
  return (
    <div className="flex flex-col gap-space-4 rounded-xl border border-dashed border-border/60 bg-muted/20 p-space-6">
      <Skeleton className="h-5 w-32" />
      <SkeletonText lines={3} />
      <span className="sr-only">{label}</span>
    </div>
  )
}
