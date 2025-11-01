import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionCardProps {
  title?: string;
  description?: string;
  children?: ReactNode;
  footer?: ReactNode;
  className?: string;
  action?: ReactNode;
}

export function SectionCard({
  title,
  description,
  children,
  footer,
  className,
  action,
}: SectionCardProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm shadow-primary/5 backdrop-blur",
        "transition-colors",
        className,
      )}
    >
      {(title || description || action) && (
        <header className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {title ? (
              <h2 className="text-xl font-semibold text-foreground/95">{title}</h2>
            ) : null}
            {description ? (
              <p className="text-sm text-muted-foreground">{description}</p>
            ) : null}
          </div>
          {action ? <div className="flex shrink-0 items-center gap-2">{action}</div> : null}
        </header>
      )}
      {children}
      {footer ? <footer className="mt-4 text-sm text-muted-foreground">{footer}</footer> : null}
    </section>
  );
}
