import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 flex flex-col">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl font-bold text-blue-600">Tinko</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/auth/signin" className="text-sm font-medium text-slate-700 hover:text-slate-900">
                Sign in
              </Link>
              <Link href="/pricing" className="text-sm font-medium text-slate-700 hover:text-slate-900">
                Pricing
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <h1 className="text-5xl font-bold text-slate-900 mb-4">
          Welcome to <span className="text-blue-600">Tinko</span>
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mb-8">
          Recover failed payments with automation, analytics, and rules you control.
        </p>

        <div className="flex gap-4">
          <Link
            href="/auth/signup"
            className="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
          <Link
            href="/pricing"
            className="px-6 py-3 rounded-lg border border-slate-300 bg-white text-slate-900 font-medium hover:bg-slate-50 transition-colors"
          >
            View Pricing
          </Link>
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-600">
              © 2025 Tinko. All rights reserved.
            </p>
            <div className="flex gap-6">
              <Link href="/privacy" className="text-sm text-slate-600 hover:text-slate-900">
                Privacy
              </Link>
              <Link href="/terms" className="text-sm text-slate-600 hover:text-slate-900">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
