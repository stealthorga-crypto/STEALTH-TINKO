"use client";

import { PageHeader } from "@/components/ui/page-header";
import { PageDescription } from "@/components/ui/page-description";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <PageHeader>Settings</PageHeader>
        <PageDescription>
          Manage environments, alerting preferences, and billing once the integration is ready.
        </PageDescription>
      </div>

      <section className="rounded-2xl border bg-white p-6 shadow-sm">
        <div className="rounded-xl border border-dashed bg-slate-50 p-6">
          <div className="text-lg font-medium">Settings are not ready yet</div>
          <p className="mt-2 text-sm text-slate-600">
            The next sprint will introduce environment toggles, role management, and audit logging controls.
          </p>
          <div className="mt-4 inline-flex rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
            Planned for Q1
          </div>
        </div>
      </section>
    </div>
  );
}
