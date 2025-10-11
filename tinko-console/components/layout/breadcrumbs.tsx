"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Breadcrumbs() {
  const pathname = usePathname() ?? "/";
  const parts = pathname.split("/").filter(Boolean);
  const crumbs = ["Console", ...parts.slice(-1)];
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-slate-600">
      <ol className="flex items-center gap-2">
        {crumbs.map((c, i) => (
          <li key={i} className="flex items-center gap-2">
            {i > 0 && <span aria-hidden>›</span>}
            <span className={i === crumbs.length - 1 ? "text-slate-900" : ""}>{c[0]?.toUpperCase() + c.slice(1)}</span>
          </li>
        ))}
      </ol>
    </nav>
  );
}
