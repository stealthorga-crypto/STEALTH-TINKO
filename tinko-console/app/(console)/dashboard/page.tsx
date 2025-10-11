"use client";

import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { PageDescription } from "@/components/ui/page-description";

function Kpi({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <Card className="p-5">
      <div className="text-sm text-slate-600">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-500">{sub}</div>}
    </Card>
  );
}

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <PageHeader>Dashboard</PageHeader>
        <PageDescription>
          Monitor recovery performance and track next actions.
        </PageDescription>
      </div>

      {/* KPIs */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Kpi label="Recovered" value="$82.4K" sub="+12% vs last 30d" />
        <Kpi label="Active rules" value="18" sub="4 channels" />
        <Kpi label="Alerts" value="3" sub="Need review" />
        <Kpi label="Merchants" value="12" sub="Of 15 invited" />
      </section>

      {/* Split grid */}
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2 p-5">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Recovery health</h3>
            <button className="rounded-lg border px-3 py-1.5 text-sm hover:bg-slate-50">
              Refresh
            </button>
          </div>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="rounded-lg border p-3">Invoice auto-collected · Blue Finch · $1,240 · 35m ago</li>
            <li className="rounded-lg border p-3">Escalation triggered · Central Outfitters · $620 · 2h ago</li>
            <li className="rounded-lg border p-3">Promise-to-pay scheduled · Sunrise Goods · $480 · 4h ago</li>
          </ul>
        </Card>

        <Card className="p-5">
          <h3 className="font-medium">Next steps</h3>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-700">
            <li>Configure webhook for recovery events.</li>
            <li>Invite ops leads to review high-priority rules.</li>
            <li>Map merchant IDs to finance accounts.</li>
          </ul>
        </Card>
      </section>

      <Card className="p-5">
        <h3 className="font-medium">Upcoming milestones</h3>
        <p className="mt-1 text-sm text-slate-600">
          Workflow builder, billing insights, and full auth integration.
        </p>
      </Card>
    </div>
  );
}
