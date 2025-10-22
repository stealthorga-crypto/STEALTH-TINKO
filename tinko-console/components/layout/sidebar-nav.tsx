"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useI18n } from "@/lib/i18n";

const navItems = [
  { href: "/dashboard", labelKey: "nav.dashboard" },
  { href: "/rules", labelKey: "nav.rules" },
  { href: "/templates", labelKey: "nav.templates" },
  { href: "/settings", labelKey: "nav.settings" },
  { href: "/developer", labelKey: "nav.developer" },
  { href: "/help", labelKey: "nav.help" },
];

export default function SidebarNav() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <nav className="flex-1 p-4">
      <ul className="space-y-1">
        {navItems.map((item) => {
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
