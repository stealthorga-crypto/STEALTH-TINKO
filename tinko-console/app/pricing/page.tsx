export default function Pricing() {
  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <h1 className="text-2xl font-semibold">Pricing</h1>
        <p className="mt-2 text-slate-600">Transparent, usage-based pricing. Contact us for enterprise plans.</p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-lg font-medium">Starter</div>
            <div className="mt-1 text-sm text-slate-600">All core features to start recovering revenue.</div>
          </div>
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-lg font-medium">Growth</div>
            <div className="mt-1 text-sm text-slate-600">Higher limits, priority support, and advanced analytics.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
