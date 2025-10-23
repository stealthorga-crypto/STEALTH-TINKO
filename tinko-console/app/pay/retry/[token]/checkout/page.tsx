"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

type RecoverByToken = { ok: boolean; data?: { transaction_ref?: string; status?: string } };

export default function RetryTokenCheckoutPage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      try {
        const origin = typeof window !== "undefined" ? window.location.origin : "";
        const info = await api.get<RecoverByToken>(`/v1/recoveries/by_token/${token}`);
        if (!info?.ok || !info?.data?.transaction_ref) {
          setError("Invalid or expired link");
          return;
        }
        const ref = info.data.transaction_ref;
        const order = await api.post<{ order_id: string; key_id: string; amount: number; currency: string }>(
          "/v1/payments/razorpay/orders-public",
          { ref }
        );
        const { order_id, key_id, amount, currency } = order;
        // Load Razorpay script
        await new Promise<void>((resolve, reject) => {
          const id = "rzp-checkout-js";
          if (document.getElementById(id)) return resolve();
          const s = document.createElement("script");
          s.id = id;
          s.src = "https://checkout.razorpay.com/v1/checkout.js";
          s.onload = () => resolve();
          s.onerror = () => reject(new Error("Failed to load Razorpay"));
          document.body.appendChild(s);
        });
        const opts: any = {
          key: key_id,
          order_id,
          amount,
          currency,
          name: "Tinko Recovery",
          description: `Payment Recovery ${ref}`,
          handler: function () {
            window.location.href = `${origin}/pay/success`;
          },
          modal: {
            ondismiss: function () {
              window.location.href = `${origin}/pay/cancel`;
            },
          },
        };
        // @ts-ignore
        const rzp = new (window as any).Razorpay(opts);
        rzp.open();
      } catch (e) {
        console.error(e);
        setError("Failed to start Razorpay Checkout");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [token]);

  if (loading) return <div className="p-6">Preparing checkout…</div>;
  if (error)
    return (
      <div className="p-6">
        <h1 className="text-xl font-semibold mb-2">Unable to launch Checkout</h1>
        <p className="text-sm text-red-600 mb-4">{error}</p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={() => router.refresh()}>
          Try again
        </button>
      </div>
    );
  return null;
}
