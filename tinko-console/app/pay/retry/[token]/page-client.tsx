"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { SchedulePicker } from "@/components/SchedulePicker";

type RecoverByToken = { ok: boolean; data?: { transaction_ref?: string; attempt_id?: number } };

export function RetryTokenPageClient() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const [ref, setRef] = useState<string | null>(null);
  const [picked, setPicked] = useState<string | null>(null);
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const info = await api.get<RecoverByToken>(`/v1/recoveries/by_token/${token}`);
        if (!info?.ok || !info?.data?.transaction_ref) {
          setError("Invalid or expired recovery link");
          return;
        }
  setRef(info.data.transaction_ref);
  setAttemptId(info.data.attempt_id ?? null);
      } catch (e) {
        console.error(e);
        setError("Failed to load recovery details");
      }
    };
    run();
  }, [token]);

  const proceedToPay = () => {
    router.push(`/pay/retry/${token}/checkout`);
  };

  const saveSchedule = async () => {
    if (!picked || !attemptId) return;
    setSaving(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8010"}/v1/recoveries/${attemptId}/next_retry_at`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ next_retry_at: picked }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`Save failed: ${res.status} ${t}`);
      }
    } catch (e: any) {
      setError(e?.message ?? "Failed to save schedule");
      return;
    } finally {
      setSaving(false);
    }
  };

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold mb-2">Unable to proceed</h1>
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (!ref) return <div className="p-6">Loading…</div>;

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Choose a time or pay now</h1>
        <p className="text-sm text-slate-600">Transaction: {ref}</p>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-medium">Suggested retry windows</h2>
        <SchedulePicker refId={ref} onSelect={setPicked} />
        {picked && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-green-700">Selected: {new Date(picked).toLocaleString()}</div>
            <button
              disabled={saving}
              onClick={saveSchedule}
              className="px-3 py-1.5 bg-emerald-600 text-white rounded-md disabled:opacity-60"
            >
              {saving ? "Saving…" : "Save schedule"}
            </button>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={proceedToPay}
          className="px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          Pay now
        </button>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 border rounded-md"
        >
          Back
        </button>
      </div>
    </div>
  );
}