"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Rev = { currency: string; amount_cents: number };
type Rate = { rate: number };
type Attempts = { by_channel: Record<string, number>; by_status: Record<string, number> };

export default function Dashboard() {
  const [rev, setRev] = useState<Rev | null>(null);
  const [rate, setRate] = useState<Rate | null>(null);
  const [att, setAtt] = useState<Attempts | null>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    let stop = false;
    async function poll() {
      try {
        const [r1, r2, r3] = await Promise.all([
          api.get<Rev>("/v1/analytics/revenue_recovered"),
          api.get<Rate>("/v1/analytics/recovery_rate"),
          api.get<Attempts>("/v1/analytics/attempts_summary"),
        ]);
        if (!stop) {
          setRev(r1);
          setRate(r2);
          setAtt(r3);
          setErr("");
        }
      } catch (e: any) {
        if (!stop) {
          if (e instanceof ApiError) {
            setErr(`${e.message} (${e.status})`);
          } else {
            setErr(e?.message ?? "Unknown error");
          }
        }
      } finally {
        if (!stop) setTimeout(poll, 15000);
      }
    }
    poll();
    return () => {
      stop = true;
    };
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
