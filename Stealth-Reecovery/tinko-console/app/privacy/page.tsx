import Link from "next/link";

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-bold text-slate-900 mb-8">Privacy Policy</h1>
          
          <div className="prose prose-slate max-w-none">
            <p className="text-slate-600 mb-6">Last updated: October 17, 2025</p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Introduction</h2>
            <p className="text-slate-700 mb-4">
              This Privacy Policy describes how Tinko collects, uses, and protects your information.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Information We Collect</h2>
            <p className="text-slate-700 mb-4">
              We collect information you provide directly to us, including account information,
              payment data, and usage analytics.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">How We Use Your Information</h2>
            <p className="text-slate-700 mb-4">
              We use the information we collect to provide, maintain, and improve our services,
              process transactions, and communicate with you.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Data Security</h2>
            <p className="text-slate-700 mb-4">
              We implement industry-standard security measures to protect your information from
              unauthorized access, disclosure, or destruction.
            </p>

            <h2 className="text-2xl font-semibold text-slate-900 mb-4 mt-8">Contact Us</h2>
            <p className="text-slate-700 mb-4">
              If you have questions about this Privacy Policy, please contact us at privacy@tinko.in
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
