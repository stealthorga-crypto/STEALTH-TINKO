"use client";

import { useEffect, useState } from "react";

type Rev = { currency: string; amount_cents: number };
type Rate = { rate: number };
type Attempts = { by_channel: Record<string, number>; by_status: Record<string, number> };

export default function Dashboard() {
  // USING MOCK DATA FOR TESTING - NO BACKEND REQUIRED
  const [rev, setRev] = useState<Rev | null>(null);
  const [rate, setRate] = useState<Rate | null>(null);
  const [att, setAtt] = useState<Attempts | null>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    // Load mock data immediately
    setRev({ currency: "USD", amount_cents: 145750 }); // $1,457.50
    setRate({ rate: 0.68 }); // 68% recovery rate
    setAtt({
      by_channel: {
        email: 245,
        sms: 132,
        webhook: 89,
        manual: 34
      },
      by_status: {
        success: 312,
        failed: 98,
        pending: 90
      }
    });
    setErr("");
  }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Recovery Dashboard</h1>
      {err ? <p className="text-red-600">Error: {err}</p> : null}
      <section className="grid sm:grid-cols-3 gap-4">
        <div className="rounded-xl border p-4">
          <h2 className="font-medium">Revenue Recovered</h2>
          <p className="text-xl">
            {rev ? `${rev.currency} ${(rev.amount_cents / 100).toFixed(2)}` : "…"}
          </p>
        </div>
        <div className="rounded-xl border p-4">
          <h2 className="font-medium">Recovery Rate</h2>
          <p className="text-xl">{rate ? `${Math.round(rate.rate * 100)}%` : "…"}</p>
        </div>
        <div className="rounded-xl border p-4">
          <h2 className="font-medium">Attempts (by channel)</h2>
          <pre className="text-sm">{att ? JSON.stringify(att.by_channel, null, 2) : "…"}</pre>
        </div>
      </section>
    </main>
  );
}
