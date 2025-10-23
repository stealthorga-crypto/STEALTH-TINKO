"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function OnboardingPage() {
  // Step 1: Server-side Razorpay ping (no secrets in browser)
  // Step 2: Save minimal retry policy via /v1/retry/policies
  const [step, setStep] = useState(1);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  // Retry policy fields
  const [name, setName] = useState("Default Policy");
  const [maxRetries, setMaxRetries] = useState(3);
  const [initialDelay, setInitialDelay] = useState(60);
  const [backoffMultiplier, setBackoffMultiplier] = useState(2);
  const [maxDelay, setMaxDelay] = useState(1440);
  const [channels, setChannels] = useState<string[]>(["email"]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const toggleChannel = (c: string) => {
    setChannels(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  const testRazorpay = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      await api.get("/v1/payments/razorpay/ping");
      setTestResult("Razorpay connection OK");
      setStep(2);
    } catch (e) {
      setTestResult("Razorpay not configured. Set RAZORPAY_KEY_ID/RAZORPAY_KEY_SECRET and try again.");
    } finally {
      setTesting(false);
    }
  };

  const savePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post("/v1/retry/policies", {
        name,
        max_retries: Number(maxRetries),
        initial_delay_minutes: Number(initialDelay),
        backoff_multiplier: Number(backoffMultiplier),
        max_delay_minutes: Number(maxDelay),
        channels,
      });
      setSaved(true);
    } catch (e) {
      setSaved(false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-semibold text-slate-900 mb-2">Onboarding</h1>
      <p className="text-slate-600 mb-6">Two quick steps to get your console ready.</p>

      {step === 1 && (
        <div className="bg-white border rounded p-6 space-y-4">
          <h2 className="text-lg font-semibold">Step 1: Connect Razorpay</h2>
          <p className="text-sm text-slate-700">
            Server-side only: set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your API environment. This wizard does not store secrets in the browser.
          </p>
          <button
            onClick={testRazorpay}
            disabled={testing}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-60"
          >
            {testing ? "Testing…" : "Test connection"}
          </button>
          {testResult && <p className="text-sm text-slate-700">{testResult}</p>}
        </div>
      )}

      {step === 2 && (
        <div className="bg-white border rounded p-6 space-y-4">
          <h2 className="text-lg font-semibold">Step 2: Set a retry policy</h2>
          <form onSubmit={savePolicy} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Policy name</label>
              <input className="w-full border rounded px-3 py-2" value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Initial delay (min)</label>
                <input type="number" className="w-full border rounded px-3 py-2" value={initialDelay} onChange={e => setInitialDelay(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Backoff multiplier</label>
                <input type="number" step="0.1" className="w-full border rounded px-3 py-2" value={backoffMultiplier} onChange={e => setBackoffMultiplier(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Max retries</label>
                <input type="number" className="w-full border rounded px-3 py-2" value={maxRetries} onChange={e => setMaxRetries(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Max delay (min)</label>
                <input type="number" className="w-full border rounded px-3 py-2" value={maxDelay} onChange={e => setMaxDelay(Number(e.target.value))} />
              </div>
            </div>
            <div>
              <div className="block text-sm font-medium text-slate-700 mb-2">Channels</div>
              {(["email", "sms", "whatsapp"] as const).map(c => (
                <label key={c} className="inline-flex items-center gap-2 mr-6 text-sm">
                  <input type="checkbox" checked={channels.includes(c)} onChange={() => toggleChannel(c)} />
                  <span className="capitalize">{c}</span>
                </label>
              ))}
            </div>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={saving}>
              {saving ? "Saving…" : "Save policy"}
            </button>
            {saved && <span className="ml-3 text-sm text-green-700">Policy saved ✓</span>}
          </form>
        </div>
      )}
    </div>
  );
}
