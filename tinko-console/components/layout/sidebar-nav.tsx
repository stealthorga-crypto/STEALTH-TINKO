"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

type NavItem = { href: string; label: string };
const NAV: NavItem[] = [
	{ href: "/dashboard", label: "Dashboard" },
	{ href: "/onboarding", label: "Onboarding" },
	{ href: "/rules", label: "Rules" },
	{ href: "/templates", label: "Templates" },
	{ href: "/developer/logs", label: "Developer" },
	{ href: "/settings", label: "Settings" },
];

export function SidebarNav() {
	const pathname = usePathname() || "/dashboard";
	return (
		<nav aria-label="Primary" className="flex-1 overflow-y-auto px-2 py-3">
			<ul className="space-y-1">
				{NAV.map((item) => {
					const active =
						pathname === item.href ||
						(item.href !== "/dashboard" && pathname.startsWith(item.href));
					return (
						<li key={item.href}>
							<Link
								href={item.href}
								aria-current={active ? "page" : undefined}
								className={clsx(
									"flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-colors outline-none focus-visible:ring-2 focus-visible:ring-blue-600",
									active
										? "bg-blue-50 text-blue-700 font-semibold"
										: "text-slate-700 hover:bg-slate-100"
								)}
							>
								<span className="truncate">{item.label}</span>
							</Link>
						</li>
					);
				})}
			</ul>
			<div className="mt-4 rounded-xl border p-3 text-sm text-slate-600">
				<div className="font-medium mb-1">Need help?</div>
				Review onboarding and rules to start syncing merchant data.
			</div>
		</nav>
	);
}
