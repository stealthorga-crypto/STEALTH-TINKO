"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function CheckoutRedirectPage({ params }: { params: { token: string } }) {
  const router = useRouter();
  const { token } = params; // using consistent dynamic segment name [token]
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const go = async () => {
      try {
        const origin = typeof window !== "undefined" ? window.location.origin : "";
        const res = await api.post<{ ok: boolean; data: { url: string } }>(
          "/v1/payments/stripe/checkout",
          {
            transaction_ref: token, // treated as ref value in this route
            success_url: `${origin}/pay/success`,
            cancel_url: `${origin}/pay/cancel`,
          }
        );
        if (res?.data?.url) {
          window.location.href = res.data.url;
          return;
        }
        setError("No checkout URL returned");
      } catch (e) {
        console.error(e);
        setError("Failed to create checkout session");
      } finally {
        setLoading(false);
      }
    };
    go();
  }, [token]);

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-slate-700">Preparing checkout…</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-2">Unable to redirect to Checkout</h1>
      {error && <p className="text-sm text-red-600 mb-4">{error}</p>}
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => router.refresh()}
      >
        Try again
      </button>
    </div>
  );
}
