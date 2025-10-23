"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n";

type NavItem = { href: string; labelKey: string; roles?: Array<"admin" | "analyst" | "operator"> };
const navItems: NavItem[] = [
  { href: "/dashboard", labelKey: "nav.dashboard", roles: ["admin", "analyst", "operator"] },
  { href: "/rules", labelKey: "nav.rules", roles: ["admin", "analyst"] },
  { href: "/templates", labelKey: "nav.templates", roles: ["admin", "analyst"] },
  { href: "/settings", labelKey: "nav.settings", roles: ["admin"] },
  { href: "/developer", labelKey: "nav.developer", roles: ["admin", "analyst"] },
  { href: "/help", labelKey: "nav.help", roles: ["admin", "analyst", "operator"] },
];

export default function SidebarNav() {
  const pathname = usePathname();
  const { t } = useI18n();
  let role: "admin" | "analyst" | "operator" = "operator";
  if (typeof window !== "undefined") {
    const r = (window.localStorage.getItem("user_role") || "operator").toLowerCase();
    if (r === "admin" || r === "analyst" || r === "operator") {
      role = r as any;
    }
  }

  return (
    <nav className="flex-1 p-4">
      <ul className="space-y-1">
        {navItems
          .filter((it) => !it.roles || it.roles.includes(role))
          .map((item) => {
          const isActive = pathname === item.href;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                {t(item.labelKey)}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
