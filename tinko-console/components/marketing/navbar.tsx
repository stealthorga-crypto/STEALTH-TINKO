"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NavLink = ({ href, children }: { href: string; children: React.ReactNode }) => {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link
      href={href}
      className={`rounded-xl px-3 py-2 text-sm hover:bg-slate-100 ${active ? "text-slate-900" : "text-slate-600"}`}
    >
      {children}
    </Link>
  );
};

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-semibold">T</div>
          <span className="font-semibold">Tinko</span>
        </Link>
        <nav className="ml-6 hidden items-center gap-1 md:flex">
          <a href="#benefits" className="rounded-xl px-3 py-2 text-sm text-slate-600 hover:bg-slate-100">Benefits</a>
          <NavLink href="/pricing">Pricing</NavLink>
          <NavLink href="/privacy">Privacy</NavLink>
          <NavLink href="/terms">Terms</NavLink>
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <Link
            href="/auth/signin"
            className="rounded-xl border px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Login
          </Link>
          <Link
            href="/auth/signin"
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
