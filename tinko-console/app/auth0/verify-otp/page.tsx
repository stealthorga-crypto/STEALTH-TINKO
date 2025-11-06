"use client";

import { useState, FormEvent, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

function VerifyOTPContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [otp, setOtp] = useState("");
  const [resending, setResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const email = searchParams.get("email") || "";
  const phone = searchParams.get("phone") || "";

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/auth0/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          phone,
          otp,
          channel: process.env.NEXT_PUBLIC_OTP_CHANNEL || "email",
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 429) {
          throw new Error(`Too many attempts. Please wait ${data.retryAfter} seconds.`);
        }
        throw new Error(data.error || "Failed to verify OTP");
      }

      // Success - redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setError(null);
    setResending(true);

    try {
      const res = await fetch("/api/auth0/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          phone,
          channel: process.env.NEXT_PUBLIC_OTP_CHANNEL || "email",
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 429) {
          throw new Error(`Too many requests. Please wait ${data.retryAfter} seconds.`);
        }
        throw new Error(data.error || "Failed to resend OTP");
      }

      // Set cooldown to prevent spam
      setResendCooldown(60);
      setError("New OTP sent successfully!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to resend OTP");
    } finally {
      setResending(false);
    }
  };

  const handleOTPInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, "").slice(0, 6);
    setOtp(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="text-3xl font-bold text-indigo-600">
            Tinko
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 mt-4">Verify OTP</h1>
          <p className="text-slate-600 mt-2">Enter the 6-digit code we sent to</p>
          <p className="text-slate-900 font-medium mt-1">{email || phone}</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="otp" className="block text-sm font-medium text-slate-700 mb-2 text-center">
                Verification Code
              </label>
              <input
                id="otp"
                name="otp"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                value={otp}
                onChange={handleOTPInput}
                required
                disabled={loading}
                autoFocus
                className="w-full px-4 py-4 text-center text-2xl font-mono tracking-[0.5em] border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed"
                placeholder="------"
              />
              <p className="mt-2 text-xs text-slate-500 text-center">
                Enter the 6-digit code from your {process.env.NEXT_PUBLIC_OTP_CHANNEL === "sms" ? "SMS" : "email"}
              </p>
            </div>

            {error && (
              <div className={`border rounded-lg p-4 ${
                error.includes("successfully") 
                  ? "bg-green-50 border-green-200" 
                  : "bg-red-50 border-red-200"
              }`}>
                <div className="flex items-start">
                  <svg 
                    className={`w-5 h-5 mt-0.5 mr-2 ${
                      error.includes("successfully") ? "text-green-600" : "text-red-600"
                    }`} 
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    {error.includes("successfully") ? (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    ) : (
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    )}
                  </svg>
                  <p className={`text-sm ${
                    error.includes("successfully") ? "text-green-800" : "text-red-800"
                  }`}>
                    {error}
                  </p>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || otp.length !== 6}
              className="w-full px-4 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 transition-colors disabled:bg-indigo-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Verifying...
                </>
              ) : (
                "Verify & Continue"
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600 mb-2">Didn&apos;t receive the code?</p>
            <button
              onClick={handleResendOTP}
              disabled={resending || resendCooldown > 0}
              className="text-indigo-600 hover:text-indigo-700 font-medium text-sm disabled:text-slate-400 disabled:cursor-not-allowed"
            >
              {resending ? "Sending..." : resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend OTP"}
            </button>
          </div>

          <div className="mt-6 text-center">
            <Link href="/auth0/signup" className="text-sm text-slate-600 hover:text-slate-900">
              ← Back to signup
            </Link>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-slate-600">
          <p>Secured by Auth0 • Passwordless Authentication</p>
        </div>
      </div>
    </div>
  );
}

export default function Auth0VerifyOTPPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    }>
      <VerifyOTPContent />
    </Suspense>
  );
}
