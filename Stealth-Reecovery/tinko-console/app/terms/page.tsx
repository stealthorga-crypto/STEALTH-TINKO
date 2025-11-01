import Link from "next/link";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="text-xl font-bold text-blue-600">
              Tinko
            </Link>
          </div>
        </div>
      </nav>

      <main className="py-16 px-4">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-4xl font-bold text-slate-900 mb-8">Terms of Service</h1>
          
          <div className="prose prose-slate max-w-none">
            <p className="text-slate-600 mb-6">Last updated: October 17, 2025</p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Acceptance of Terms</h2>
            <p className="text-slate-700 mb-4">
              By accessing or using Tinko&apos;s services, you agree to be bound by these Terms of Service.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Use of Services</h2>
            <p className="text-slate-700 mb-4">
              You agree to use our services only for lawful purposes and in accordance with these Terms.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Account Responsibilities</h2>
            <p className="text-slate-700 mb-4">
              You are responsible for maintaining the confidentiality of your account credentials
              and for all activities under your account.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Limitation of Liability</h2>
            <p className="text-slate-700 mb-4">
              Tinko shall not be liable for any indirect, incidental, special, or consequential
              damages arising from your use of our services.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Contact</h2>
            <p className="text-slate-700 mb-4">
              For questions about these Terms, contact us at legal@tinko.in
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
