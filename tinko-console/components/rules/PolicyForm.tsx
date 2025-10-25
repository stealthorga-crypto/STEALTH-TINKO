"use client";

import { useState } from "react";
import type { RetryPolicyInput } from "@/lib/retryPolicies";

export function PolicyForm({ onSubmit }: { onSubmit: (input: RetryPolicyInput) => Promise<void> | void }) {
  const [name, setName] = useState("Default Policy");
  const [maxRetries, setMaxRetries] = useState(3);
  const [initialDelay, setInitialDelay] = useState(60);
  const [backoff, setBackoff] = useState(2);
  const [maxDelay, setMaxDelay] = useState(1440);
  const [channels, setChannels] = useState<string[]>(["email"]);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const toggle = (c: string) => {
    setChannels((prev) => (prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    // validation
    if (!name.trim()) return setErr("Name is required");
    if (maxRetries < 1 || maxRetries > 10) return setErr("Max retries must be 1-10");
    if (initialDelay < 0) return setErr("Initial delay must be >= 0");
    if (backoff < 1) return setErr("Backoff multiplier must be >= 1");
    if (maxDelay < initialDelay) return setErr("Max delay must be >= initial delay");
    const input: RetryPolicyInput = {
      name,
      max_retries: Number(maxRetries),
      initial_delay_minutes: Number(initialDelay),
      backoff_multiplier: Number(backoff),
      max_delay_minutes: Number(maxDelay),
      enabled_channels: channels,
    };
    setSubmitting(true);
    try {
      await Promise.resolve(onSubmit(input));
      // reset minimal
      setName("Default Policy");
      setMaxRetries(3);
      setInitialDelay(60);
      setBackoff(2);
      setMaxDelay(1440);
      setChannels(["email"]);
    } catch (e: any) {
      setErr(e?.message ?? "Failed to create policy");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {err && <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{err}</div>}
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-900">Name</label>
        <input
          className="w-full rounded border border-slate-300 px-3 py-2"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Policy name"
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium">Max retries (1-10)</label>
          <input
            type="number"
            min={1}
            max={10}
            className="w-full rounded border border-slate-300 px-3 py-2"
            value={maxRetries}
            onChange={(e) => setMaxRetries(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Initial delay (min)</label>
          <input
            type="number"
            min={0}
            className="w-full rounded border border-slate-300 px-3 py-2"
            value={initialDelay}
            onChange={(e) => setInitialDelay(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Backoff multiplier (≥1)</label>
          <input
            type="number"
            min={1}
            step="0.1"
            className="w-full rounded border border-slate-300 px-3 py-2"
            value={backoff}
            onChange={(e) => setBackoff(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Max delay (min)</label>
          <input
            type="number"
            min={0}
            className="w-full rounded border border-slate-300 px-3 py-2"
            value={maxDelay}
            onChange={(e) => setMaxDelay(Number(e.target.value))}
          />
        </div>
      </div>
      <div>
        <div className="mb-1 block text-sm font-medium">Channels</div>
        {(["email", "sms", "whatsapp"] as const).map((c) => (
          <label key={c} className="mr-4 inline-flex items-center gap-2 text-sm">
            <input type="checkbox" checked={channels.includes(c)} onChange={() => toggle(c)} />
            <span className="capitalize">{c}</span>
          </label>
        ))}
      </div>
      <button
        type="submit"
        className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-60"
        disabled={submitting}
      >
        {submitting ? "Saving…" : "Create policy"}
      </button>
    </form>
  );
}
