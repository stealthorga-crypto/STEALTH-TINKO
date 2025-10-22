"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Revenue = { total_recovered: number; currency: string };
type Rate = { recovery_rate: number; total_attempts: number; successful: number };
type Category = { category: string; count: number };

export default function DashboardPage() {
  const [revenue, setRevenue] = useState<Revenue | null>(null);
  const [rate, setRate] = useState<Rate | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const [rev, rr, cats] = await Promise.all([
        api.get<Revenue>("/v1/analytics/revenue_recovered"),
        api.get<Rate>("/v1/analytics/recovery_rate"),
        api.get<Category[]>("/v1/analytics/failure_categories"),
      ]);
      setRevenue(rev);
      setRate(rr);
      setCategories(cats);
      setError(null);
    } catch (e) {
      console.warn(e);
      setError("Failed to load analytics");
    }
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 20000);
    return () => clearInterval(id);
  }, []);

  const formatMoney = (amount: number | undefined, currency: string | undefined) => {
    if (amount == null) return "-";
    const val = amount / 100;
    return new Intl.NumberFormat(undefined, { style: "currency", currency: (currency || "USD").toUpperCase() }).format(val);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Dashboard</h1>

      {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Recovered Amount</p>
          <p className="text-3xl font-bold text-blue-600">{formatMoney(revenue?.total_recovered, revenue?.currency)}</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Recovery Rate</p>
          <p className="text-3xl font-bold text-slate-900">{rate ? `${rate.recovery_rate}%` : "-"}</p>
          <p className="text-xs text-slate-600 mt-2">{rate ? `${rate.successful}/${rate.total_attempts} completed` : ""}</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-900 mb-3">Failure categories</p>
          <div className="space-y-2 max-h-40 overflow-auto">
            {categories.map(c => (
              <div key={c.category} className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{c.category}</span>
                <span className="text-slate-900 font-medium">{c.count}</span>
              </div>
            ))}
            {categories.length === 0 && <div className="text-sm text-slate-500">No data yet</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
