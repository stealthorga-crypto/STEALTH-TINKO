"use client";

import React, { useEffect, useState } from "react";
// Console Settings: Retry Policy editor wired to /v1/retry API
import { api } from "@/lib/api";

type Policy = {
  id: number;
  org_id: number;
  name: string;
  max_retries: number;
  initial_delay_minutes: number;
  backoff_multiplier: number;
  max_delay_minutes: number;
  enabled_channels: string[];
  is_active: boolean;
};

export default function RetryPolicyPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const [name, setName] = useState("Default Policy");
  const [maxRetries, setMaxRetries] = useState(3);
  const [initialDelay, setInitialDelay] = useState(60);
  const [backoffMultiplier, setBackoffMultiplier] = useState(2);
  const [maxDelay, setMaxDelay] = useState(1440);
  const [channels, setChannels] = useState<string[]>(["email"]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const active = await api.get<Policy | null>("/v1/retry/policies/active");
        if (!cancelled && active) {
          setName(active.name || "Active Policy");
          setMaxRetries(active.max_retries);
          setInitialDelay(active.initial_delay_minutes);
          setBackoffMultiplier(active.backoff_multiplier);
          setMaxDelay(active.max_delay_minutes);
          setChannels(active.enabled_channels ?? ["email"]);
        }
      } catch (e) {
        console.warn("Failed to load active retry policy", e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const toggleChannel = (c: string) => {
    setChannels(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await api.post<Policy>("/v1/retry/policies", {
        name,
        max_retries: Number(maxRetries),
        initial_delay_minutes: Number(initialDelay),
        backoff_multiplier: Number(backoffMultiplier),
        max_delay_minutes: Number(maxDelay),
        channels, // backend accepts alias
      });
      setMessage("Policy saved");
    } catch (e) {
      console.error(e);
      setMessage("Failed to save policy");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-slate-900 mb-4">Retry Policy</h1>
      <p className="text-slate-600 mb-6">Configure how and when recovery notifications are retried.</p>

      {loading ? (
        <div>Loading…</div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-6 max-w-xl">
          <div className="bg-white rounded-lg border p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Policy name</label>
              <input className="w-full border rounded px-3 py-2" value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Initial delay (min)</label>
                <input type="number" min={1} className="w-full border rounded px-3 py-2" value={initialDelay} onChange={e => setInitialDelay(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Backoff multiplier</label>
                <input type="number" min={1} step="0.1" className="w-full border rounded px-3 py-2" value={backoffMultiplier} onChange={e => setBackoffMultiplier(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Max retries</label>
                <input type="number" min={1} className="w-full border rounded px-3 py-2" value={maxRetries} onChange={e => setMaxRetries(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Max delay (min)</label>
                <input type="number" min={1} className="w-full border rounded px-3 py-2" value={maxDelay} onChange={e => setMaxDelay(Number(e.target.value))} />
              </div>
            </div>
            <div>
              <div className="block text-sm font-medium text-slate-700 mb-2">Channels</div>
              <div className="flex items-center gap-6">
                {(["email", "sms", "whatsapp"] as const).map((c) => (
                  <label key={c} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" checked={channels.includes(c)} onChange={() => toggleChannel(c)} />
                    <span className="capitalize">{c}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-60">
              {saving ? "Saving…" : "Save"}
            </button>
            {message && <span className="text-sm text-slate-700">{message}</span>}
          </div>
        </form>
      )}
    </div>
  );
}
