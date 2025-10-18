"use client";
import { usePathname } from "next/navigation";

export function Breadcrumbs() {
  const pathname = usePathname() ?? "/";
  const parts = pathname.split("/").filter(Boolean);
  const crumbs = ["Console", ...parts.slice(-1)];
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
      <ol className="flex items-center gap-2">
        {crumbs.map((c, i) => (
          <li key={i} className="flex items-center gap-2">
            {i > 0 && <span aria-hidden className="text-border">›</span>}
            <span className={i === crumbs.length - 1 ? "text-foreground font-medium" : ""}>{c[0]?.toUpperCase() + c.slice(1)}</span>
          </li>
        ))}
      </ol>
    </nav>
  );
}
