"use client";

import Link from "next/link";
import SidebarNav from "./sidebar-nav";
import { useEffect, useState } from "react";
import { useI18n } from "@/lib/i18n";

export default function Shell({ children }: { children: React.ReactNode }) {
  const [orgName, setOrgName] = useState<string>("Organization");
  const [userEmail, setUserEmail] = useState<string>("user@example.com");
  const { t } = useI18n();
  // If OAuth callback added auth_token as query param, store it once
  useEffect(() => {
    try {
      if (typeof window !== "undefined") {
        const url = new URL(window.location.href);
        const tok = url.searchParams.get("auth_token");
        if (tok) {
          window.localStorage.setItem("auth_token", tok);
          document.cookie = `authjs.session-token=${encodeURIComponent(tok)}; path=/; samesite=lax`;
          // Clean token from URL
          url.searchParams.delete("auth_token");
          window.history.replaceState({}, "", url.toString());
        }
      }
    } catch {}
  }, []);
  useEffect(() => {
    try {
      if (typeof window !== "undefined") {
        const o = window.localStorage.getItem("org_name");
        const e = window.localStorage.getItem("user_email");
        if (o) setOrgName(o);
        if (e) setUserEmail(e);
      }
    } catch {}
  }, []);
  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Tinko
          </Link>
        </div>
        <SidebarNav />
        <div className="mt-auto p-6 border-t border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-sm font-medium text-blue-600">U</span>
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-900">{orgName}</p>
              <p className="text-slate-600">{userEmail}</p>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-slate-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Console</h2>
            <div className="flex items-center gap-4">
              <select
                className="text-sm border border-slate-300 rounded px-2 py-1"
                defaultValue={typeof window !== "undefined" ? (localStorage.getItem("locale") || "en") : "en"}
                onChange={(e) => {
                  try {
                    localStorage.setItem("locale", e.target.value);
                    location.reload();
                  } catch {}
                }}
              >
                <option value="en">EN</option>
                <option value="ta">TA</option>
                <option value="hi">HI</option>
              </select>
              <Link href="/help" className="text-sm text-slate-600 hover:text-slate-900">
                {t("nav.help")}
              </Link>
            </div>
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
