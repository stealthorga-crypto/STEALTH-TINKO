"use client";

import { useI18n } from "@/lib/i18n";
import Link from "next/link";

export default function HelpPage() {
  const { t } = useI18n();
  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">{t("help.title")}</h1>
        <p className="text-sm text-slate-600 mt-1">
          Tinko Recovery — quick tips and references.
        </p>
      </div>

      <section className="space-y-2">
        <h2 className="text-lg font-medium">{t("help.onboarding.title")}</h2>
        <p className="text-slate-700">{t("help.onboarding.stripe")}</p>
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-medium">{t("help.retryPolicy.title")}</h2>
        <p className="text-slate-700">{t("help.retryPolicy.desc")}</p>
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-medium">{t("help.troubleshooting.title")}</h2>
        <ul className="list-disc pl-6 text-slate-700">
          <li>Notifications not sending? Verify SMTP and Redis are reachable.</li>
          <li>Checkout not redirecting? Check STRIPE_SECRET_KEY and network console.</li>
          <li>Webhooks failing? Ensure STRIPE_WEBHOOK_SECRET matches and the endpoint is accessible.</li>
        </ul>
      </section>

      <section className="space-x-4">
        <Link href="/docs" className="text-blue-600 underline">
          {t("help.links.docs")}
        </Link>
        <Link href="/contact" className="text-blue-600 underline">
          {t("help.links.support")}
        </Link>
      </section>
    </div>
  );
}
