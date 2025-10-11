import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function PageDescription({ children, className }: PageDescriptionProps) {
  return (
    <p className={cn("text-base text-muted-foreground", className)} style={{ fontSize: "clamp(0.95rem, 0.9vw + .4rem, 1.05rem)" }}>
      {children}
    </p>
  );
}
