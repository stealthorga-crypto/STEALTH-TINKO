"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function CheckoutRedirectPage({ params }: { params: { ref: string } }) {
  const router = useRouter();
  const { ref } = params;
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const go = async () => {
      try {
        const allow = (process.env.NEXT_PUBLIC_ALLOW_RAZORPAY_CHECKOUT || "").toLowerCase();
        const isAllowed = ["1", "true", "yes", "on"].includes(allow);
        if (!isAllowed) {
          setError("Checkout disabled by policy");
          return;
        }
        const origin = typeof window !== "undefined" ? window.location.origin : "";
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
        return;
      } catch (e) {
        console.error(e);
        setError("Failed to start Razorpay Checkout");
      } finally {
        setLoading(false);
      }
    };
    go();
  }, [ref]);

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-slate-700">Preparing checkout…</p>
      </div>
    );
  }

  return (
    <div className="p-6">
  <h1 className="text-xl font-semibold mb-2">Unable to launch Checkout</h1>
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
