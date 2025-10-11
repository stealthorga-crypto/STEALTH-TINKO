interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Loading data" }: LoadingStateProps) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-dashed border-border/60 bg-muted/30 p-6">
      <div className="h-4 w-32 animate-pulse rounded-full bg-muted" aria-hidden />
      <div className="h-3 w-full animate-pulse rounded-full bg-muted/80" aria-hidden />
      <div className="h-3 w-2/3 animate-pulse rounded-full bg-muted/70" aria-hidden />
      <span className="sr-only">{label}</span>
    </div>
  );
}
