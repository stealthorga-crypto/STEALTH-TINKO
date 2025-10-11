// app/page.tsx
import Link from "next/link";
import Navbar from "@/components/marketing/navbar";
import Footer from "@/components/marketing/footer";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 flex flex-col">
      <Navbar />
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <h1 className="text-4xl sm:text-5xl font-semibold text-slate-900">
          Welcome to <span className="text-blue-700">Tinko</span>
        </h1>
        <p className="mt-3 text-slate-600 max-w-xl">
          Recover failed payments with automation, analytics, and rules you control.
        </p>

        <div className="mt-8 grid gap-4 w-full max-w-sm">
          <Link href="/auth/signup" className="rounded-xl border border-blue-200 bg-blue-50 py-3 font-medium text-blue-700 hover:bg-blue-100">
            Sign up
          </Link>
          <Link href="/auth/signin" className="rounded-xl bg-blue-700 text-white py-3 font-medium hover:bg-blue-800">
            Sign in
          </Link>
          <Link href="/guest" className="rounded-xl border border-slate-200 bg-white py-3 font-medium text-slate-800 hover:bg-slate-50">
            Continue as Guest
          </Link>
        </div>
      </main>
      <Footer />
    </div>
  );
}
