import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div className="flex items-center gap-2">
          <div className="grid h-7 w-7 place-items-center rounded-lg bg-blue-600 text-white text-xs font-semibold">T</div>
          <span>Tinko</span>
          <span className="text-slate-400">•</span>
          <span>© {new Date().getFullYear()}</span>
        </div>
        <nav className="flex items-center gap-4">
          <Link href="/pricing" className="hover:text-slate-900">Pricing</Link>
          <Link href="/privacy" className="hover:text-slate-900">Privacy</Link>
          <Link href="/terms" className="hover:text-slate-900">Terms</Link>
          <a href="mailto:hello@tinko.in" className="hover:text-slate-900">Contact</a>
        </nav>
      </div>
    </footer>
  );
}

export default Footer;
