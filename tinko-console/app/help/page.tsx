"use client";

import { useI18n } from "@/lib/i18n";

export default function HelpPage() {
  const { t } = useI18n();
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">{t("help.title")}</h1>
      <section className="rounded-xl border p-4">
        <h2 className="text-lg font-semibold mb-2">Onboarding</h2>
        <p className="text-slate-700 text-sm">
          Configure your Razorpay keys in the backend, then create a recovery attempt to test payer flow.
        </p>
      </section>
      <section className="rounded-xl border p-4">
        <h2 className="text-lg font-semibold mb-2">Dashboards</h2>
        <p className="text-slate-700 text-sm">
          View KPIs in the Dashboard; metrics update every 20 seconds.
        </p>
      </section>
      <section className="rounded-xl border p-4">
        <h2 className="text-lg font-semibold mb-2">Languages</h2>
        <p className="text-slate-700 text-sm">Use the language switcher in the top bar (EN/TA/HI).</p>
      </section>
    </div>
  );
}
