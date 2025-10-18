"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
// Checkout flow: simple redirect button using backend session

type VerifyResponse = {
  ok: boolean;
  data: null | { transaction_ref?: string; status?: string };
  error: null | { code: string; message: string };
};

export default function RetryPage() {
  const params = useParams<{ token: string }>();
  const token = params?.token;
  const [state, setState] = useState<"loading" | "valid" | "expired" | "used" | "invalid" | "error">("loading");
  const [txnRef, setTxnRef] = useState<string | undefined>();
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    if (!token) return;

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const verify = async () => {
      try {
        const res = await fetch(`${apiBase}/v1/recoveries/by_token/${token}`);
        const json: VerifyResponse = await res.json();
        if (json.ok) {
          setTxnRef(json.data?.transaction_ref);
          setState("valid");
          // fire open marker idempotently
          fetch(`${apiBase}/v1/recoveries/by_token/${token}/open`, { method: "POST" }).catch(() => {});
        } else {
          const code = json.error?.code;
          if (code === "EXPIRED") setState("expired");
          else if (code === "USED") setState("used");
          else if (code === "NOT_FOUND") setState("invalid");
          else {
            setMessage(json.error?.message || "Unexpected error");
            setState("error");
          }
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Network error";
        setMessage(msg);
        setState("error");
      }
    };
    verify();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        {state === "loading" && <p className="text-slate-600">Checking your link…</p>}

        {state === "valid" && (
          <div className="space-y-4">
            <h1 className="text-xl font-semibold text-slate-900">Payment recovery</h1>
            <p className="text-slate-700">We found your recovery link.</p>
            {txnRef && (
              <p className="text-sm text-slate-600">Reference: <span className="font-mono">{txnRef}</span></p>
            )}
            {token && txnRef ? (
              <PayActions txnRef={txnRef} />
            ) : (
              <p className="text-slate-600">Preparing payment…</p>
            )}
          </div>
        )}

        {state === "expired" && (
          <div className="space-y-2">
            <h1 className="text-xl font-semibold text-slate-900">Link expired</h1>
            <p className="text-slate-700">Please request a new payment link from the merchant.</p>
          </div>
        )}

        {state === "used" && (
          <div className="space-y-2">
            <h1 className="text-xl font-semibold text-slate-900">Link already used</h1>
            <p className="text-slate-700">This link was already used. If you need help, contact support.</p>
          </div>
        )}

        {state === "invalid" && (
          <div className="space-y-2">
            <h1 className="text-xl font-semibold text-slate-900">Invalid link</h1>
            <p className="text-slate-700">We couldn&apos;t find this link. Check the URL and try again.</p>
          </div>
        )}

        {state === "error" && (
          <div className="space-y-2">
            <h1 className="text-xl font-semibold text-slate-900">Something went wrong</h1>
            <p className="text-slate-700">{message || "Please try again."}</p>
            <button onClick={() => location.reload()} className="w-full rounded-lg border border-slate-300 py-2">
              Retry
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function PayActions({ txnRef }: { txnRef: string }) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const successUrl = typeof window !== "undefined" ? window.location.origin + "/pay/retry/success" : "https://example.com/success";
  const cancelUrl = typeof window !== "undefined" ? window.location.href : "https://example.com/cancel";

  const start = async () => {
    setLoading(true);
    setErr(null);
    try {
      // Demo mode: if NEXT_PUBLIC_PAYMENTS_DEMO=true, simulate success without backend/Stripe
      if (process.env.NEXT_PUBLIC_PAYMENTS_DEMO === "true") {
        await new Promise((r) => setTimeout(r, 800));
        window.location.href = successUrl;
        return;
      }
      const r = await fetch(`${apiBase}/v1/payments/stripe/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_ref: txnRef, success_url: successUrl, cancel_url: cancelUrl }),
      });
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      const url = j?.data?.url as string | undefined;
      if (!url) throw new Error("Missing checkout url");
      window.location.href = url;
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Failed to start checkout");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      {err && <p className="text-red-600 text-sm">{err}</p>}
      <div className="grid gap-2">
        <button onClick={start} disabled={loading} className="w-full rounded-lg bg-blue-600 text-white py-2 disabled:opacity-60">
          {loading ? "Redirecting…" : "Continue to payment"}
        </button>
        {process.env.NEXT_PUBLIC_PAYMENTS_DEMO !== "true" && (
          <p className="text-xs text-slate-500 text-center">Set NEXT_PUBLIC_PAYMENTS_DEMO=true to simulate payment without keys.</p>
        )}
      </div>
    </div>
  );
}
