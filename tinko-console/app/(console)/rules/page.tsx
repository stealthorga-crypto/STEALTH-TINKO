"use client";

import { useEffect, useMemo, useState } from "react";
import { PolicyForm } from "../../../components/rules/PolicyForm";
import { PolicyList } from "../../../components/rules/PolicyList";
import {
  listPolicies,
  getActivePolicy,
  createPolicy,
  deletePolicy,
  type RetryPolicy,
  type RetryPolicyInput,
} from "../../../lib/retryPolicies";

export default function RulesPage() {
  const [policies, setPolicies] = useState<RetryPolicy[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const sorted = useMemo(() => {
    return [...policies].sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
  }, [policies]);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const [list, active] = await Promise.all([listPolicies(), getActivePolicy()]);
      setPolicies(list);
      setActiveId(active?.id ?? null);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load retry policies");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const onCreate = async (input: RetryPolicyInput) => {
    setError(null);
    // optimistic: add temp item
    const temp: RetryPolicy = {
      id: Math.floor(Math.random() * 1e9) * -1, // negative temp id
      org_id: 0,
      name: input.name,
      max_retries: input.max_retries,
      initial_delay_minutes: input.initial_delay_minutes,
      backoff_multiplier: input.backoff_multiplier,
      max_delay_minutes: input.max_delay_minutes,
      enabled_channels: input.enabled_channels ?? ["email"],
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setPolicies((prev) => [temp, ...prev]);
    try {
      const created = await createPolicy(input);
      // replace temp with real
      setPolicies((prev) => [created, ...prev.filter((p) => p.id !== temp.id)]);
      setActiveId(created.id);
    } catch (e: any) {
      // revert
      setPolicies((prev) => prev.filter((p) => p.id !== temp.id));
      setError(e?.message ?? "Failed to create policy");
    }
  };

  const onDelete = async (id: number) => {
    const prev = policies;
    setPolicies((cur) => cur.filter((p) => p.id !== id));
    try {
      await deletePolicy(id);
      if (activeId === id) setActiveId(null);
    } catch (e: any) {
      // revert
      setPolicies(prev);
      setError(e?.message ?? "Failed to delete policy");
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Retry Policies</h1>
      {error && (
        <div className="mb-4 rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <div className="rounded-lg border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <h2 className="text-lg font-semibold">Policies</h2>
              {loading && <span className="text-xs text-slate-500">Loading…</span>}
            </div>
            <PolicyList
              items={sorted}
              activeId={activeId}
              onDelete={onDelete}
              onRefresh={refresh}
            />
          </div>
        </div>
        <div>
          <div className="rounded-lg border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-lg font-semibold">Create Policy</h2>
              <p className="mt-1 text-sm text-slate-600">
                Configure exponential backoff. Only one policy is active at a time; creating a new policy deactivates the previous one.
              </p>
            </div>
            <div className="p-4">
              <PolicyForm onSubmit={onCreate} />
            </div>
          </div>
          <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
            <h3 className="mb-2 text-sm font-semibold text-slate-900">cURL examples</h3>
            <pre className="whitespace-pre-wrap break-all text-xs text-slate-700">{`
List:
curl -H "Authorization: Bearer TEST" http://127.0.0.1:8010/v1/retry/policies

Create:
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer TEST" \
  -d '{"name":"Default","max_retries":5,"initial_delay_minutes":5,"backoff_multiplier":2,"max_delay_minutes":60}' \
  http://127.0.0.1:8010/v1/retry/policies

Delete:
curl -X DELETE -H "Authorization: Bearer TEST" http://127.0.0.1:8010/v1/retry/policies/{id}
`}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
