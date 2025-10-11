"use client";

import Link from "next/link";
import { ReactNode, useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { OrgSwitcher } from "./org-switcher";
import { UserMenu } from "./user-menu";
"use client";

import Link from "next/link";
import { ReactNode, useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { OrgSwitcher } from "./org-switcher";
import { UserMenu } from "./user-menu";
import { Breadcrumbs } from "./breadcrumbs";
import { SidebarNav } from "./sidebar-nav";

/** Desktop uses a CSS grid: [260px sidebar | 1fr content] — no middle gap */
export function Shell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute left-4 top-4 z-50 rounded-lg bg-white px-3 py-2 shadow"
      >
        Skip to content
      </a>

      {/* Mobile header */}
      <header className="md:hidden sticky top-0 z-40 flex h-14 items-center gap-2 border-b bg-white px-3 safe-areas">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="Open navigation">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[260px] p-0">
            <div className="flex h-14 items-center gap-2 px-4">
              <Link href="/dashboard" className="flex items-center gap-2" onClick={() => setOpen(false)}>
                <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-bold">T</div>
                <div className="font-semibold">Tinko Recovery</div>
              </Link>
            </div>
            <Separator />
            <div className="py-1">
              <SidebarNav />
            </div>
          </SheetContent>
        </Sheet>
        <Link href="/dashboard" className="font-semibold">Tinko Recovery</Link>
        <div className="ml-auto flex items-center gap-2">
          <OrgSwitcher />
          <UserMenu />
        </div>
      </header>

      {/* Desktop grid: sidebar + content */}
      <div className="hidden md:grid md:min-h-dvh md:grid-cols-[260px_1fr] md:gap-0">
        {/* Sidebar */}
        <aside className="bg-white">
          <div className="sticky top-0 bg-white">
            <div className="flex h-14 items-center gap-2 px-5">
              <Link href="/dashboard" className="flex items-center gap-2">
                <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-bold">T</div>
                <div className="font-semibold">Tinko Recovery</div>
              </Link>
            </div>
            <Separator />
          </div>
          "use client";

          import Link from "next/link";
          import { ReactNode, useState } from "react";
          import { Menu } from "lucide-react";
          import { Button } from "@/components/ui/button";
          import { Separator } from "@/components/ui/separator";
          import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
          import { OrgSwitcher } from "./org-switcher";
          import { UserMenu } from "./user-menu";
          import { Breadcrumbs } from "./breadcrumbs";
          import { SidebarNav } from "./sidebar-nav";

          /** Desktop grid [260px | 1fr] eliminates the middle gap */
          export function Shell({ children }: { children: ReactNode }) {
            const [open, setOpen] = useState(false);

            return (
              <div className="min-h-dvh bg-slate-50 text-slate-900">
                {/* Mobile header */}
                <header className="md:hidden sticky top-0 z-40 flex h-14 items-center gap-2 border-b bg-white px-3">
                  <Sheet open={open} onOpenChange={setOpen}>
                    <SheetTrigger asChild>
                      <Button variant="ghost" size="icon" aria-label="Open navigation">
                        <Menu className="h-5 w-5" />
                      </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-[260px] p-0">
                      <div className="flex h-14 items-center gap-2 px-4">
                        <Link href="/dashboard" className="flex items-center gap-2" onClick={() => setOpen(false)}>
                          <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-bold">T</div>
                          <div className="font-semibold">Tinko Recovery</div>
                        </Link>
                      </div>
                      <Separator />
                      <SidebarNav />
                    </SheetContent>
                  </Sheet>
                  <Link href="/dashboard" className="font-semibold">Tinko Recovery</Link>
                  <div className="ml-auto flex items-center gap-2">
                    <OrgSwitcher />
                    <UserMenu />
                  </div>
                </header>

                {/* Desktop grid: sidebar + content */}
                <div className="hidden md:grid md:min-h-dvh md:grid-cols-[260px_1fr]">
                  <aside className="border-r bg-white">
                    <div className="sticky top-0 bg-white">
                      <div className="flex h-14 items-center gap-2 px-5">
                        <Link href="/dashboard" className="flex items-center gap-2">
                          <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-bold">T</div>
                          <div className="font-semibold">Tinko Recovery</div>
                        </Link>
                      </div>
                      <Separator />
                    </div>
                    <SidebarNav />
                    <div className="px-5 py-3 text-xs text-slate-500">Merchant Console</div>
                  </aside>

                  <div className="flex min-h-dvh flex-col">
                    {/* Top bar — NO mx-auto / container here */}
                    <div className="sticky top-0 z-30 border-b bg-white/90 backdrop-blur">
                      <div className="px-6 py-3">
                        <div className="flex items-center gap-3">
                          <Breadcrumbs />
                          <div className="ml-auto hidden items-center gap-2 md:flex">
                            <OrgSwitcher />
                            <UserMenu />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Content — full width, left-aligned */}
                    <main id="main" className="w-full px-4 py-4 sm:px-6 sm:py-6">
                      {children}
                    </main>
                  </div>
                </div>

                {/* Mobile content */}
                <div className="md:hidden">
                  <main id="main" className="w-full px-4 py-4 sm:px-6 sm:py-6">{children}</main>
                </div>
              </div>
            );
          }
