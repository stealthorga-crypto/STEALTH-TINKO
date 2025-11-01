"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

const NavLink = ({ href, children }: { href: string; children: React.ReactNode }) => {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link
      href={href}
      className={`rounded-xl px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground ${
        active ? "text-foreground font-medium" : "text-muted-foreground"
      }`}
    >
      {children}
    </Link>
  );
};

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4 lg:px-8">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground font-bold shadow-sm transition-transform group-hover:scale-105">
            T
          </div>
          <span className="text-lg font-bold text-foreground">Tinko</span>
        </Link>
        
        <nav className="hidden items-center gap-2 md:flex">
          <Link 
            href="/#benefits" 
            className="rounded-xl px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            Benefits
          </Link>
          <NavLink href="/pricing">Pricing</NavLink>
          <NavLink href="/contact">Contact</NavLink>
        </nav>
        
        <div className="flex items-center gap-space-2">
          <Link href="/auth/signin">
            <Button variant="ghost" size="sm">
              Login
            </Button>
          </Link>
          <Link href="/auth/signin">
            <Button variant="primary" size="sm">
              Sign Up Free
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
