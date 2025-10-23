"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { SchedulePicker } from "@/components/SchedulePicker";

type RecoverByToken = { ok: boolean; data?: { transaction_ref?: string } };

export default function RetryTokenPage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const [ref, setRef] = useState<string | null>(null);
  const [picked, setPicked] = useState<string | null>(null);
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
          <div className="text-sm text-green-700">Selected: {new Date(picked).toLocaleString()}</div>
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
