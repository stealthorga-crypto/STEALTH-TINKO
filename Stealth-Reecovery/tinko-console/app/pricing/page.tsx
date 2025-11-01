import Link from "next/link";

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="text-xl font-bold text-blue-600">
              Tinko
            </Link>
            <Link href="/auth/signin" className="text-sm font-medium text-slate-700 hover:text-slate-900">
              Sign in
            </Link>
          </div>
        </div>
      </nav>

      <main className="py-16 px-4">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">Simple, Transparent Pricing</h1>
            <p className="text-xl text-slate-600">Choose the plan that works for you</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-white border border-slate-200 rounded-lg p-8">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Starter</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">$99<span className="text-base text-slate-600">/mo</span></p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Up to 1,000 recoveries/mo
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Basic templates
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Email support
                </li>
              </ul>
              <button className="w-full px-4 py-2 rounded-lg border border-blue-600 text-blue-600 font-medium hover:bg-blue-50">
                Get Started
              </button>
            </div>

            <div className="bg-blue-50 border-2 border-blue-600 rounded-lg p-8 relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                Popular
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Professional</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">$299<span className="text-base text-slate-600">/mo</span></p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Up to 5,000 recoveries/mo
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Advanced templates
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Priority support
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Custom rules
                </li>
              </ul>
              <button className="w-full px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700">
                Get Started
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-lg p-8">
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Enterprise</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">Custom</p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Unlimited recoveries
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Custom integrations
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> Dedicated support
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-700">
                  <span className="text-green-500">✓</span> SLA guarantees
                </li>
              </ul>
              <button className="w-full px-4 py-2 rounded-lg border border-blue-600 text-blue-600 font-medium hover:bg-blue-50">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
