"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState<"form" | "verify">("form");
  const [emailForVerify, setEmailForVerify] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    const form = new FormData(e.currentTarget);
    const full_name = String(form.get("name") || "");
    const email = String(form.get("email") || "");
    const password = String(form.get("password") || "");
    const org_name = String(form.get("org") || "");
    
    // Validation
    if (!full_name || !email || !password || !org_name) {
      setError("All fields are required");
      setLoading(false);
      return;
    }
    
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      setLoading(false);
      return;
    }
    
    try {
      // Start OTP registration (send code to email)
      await api.post<{ ok: boolean; message: string }>(
        "/v1/auth/register/start",
        { full_name, email, password, org_name }
      );
      setEmailForVerify(email);
      setStage("verify");
    } catch (e: any) {
      console.error("Registration error:", e);
      const errorMessage = e?.body?.detail || e?.message || "Failed to start registration. Check details and try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    const form = new FormData(e.currentTarget);
    const code = String(form.get("otp") || "");
    
    if (!code || code.length !== 6) {
      setError("Please enter a 6-digit code");
      setLoading(false);
      return;
    }
    
    try {
      await api.post<{ ok: boolean; message: string }>("/v1/auth/register/verify", { email: emailForVerify, code });
      // After verification, send user to sign-in page
      router.push("/auth/signin");
    } catch (e: any) {
      console.error("Verification error:", e);
      const errorMessage = e?.body?.detail || e?.message || "Incorrect or expired OTP. Please try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            Tinko
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 mt-4">Create your account</h1>
          <p className="text-slate-600 mt-2">Start recovering failed payments today</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
          {stage === "form" && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-900 mb-2">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                name="name"
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-900 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                name="email"
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-900 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                name="password"
                required
                minLength={8}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="org" className="block text-sm font-medium text-slate-900 mb-2">
                Organization Name
              </label>
              <input
                id="org"
                type="text"
                name="org"
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="Acme Inc."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Sending..." : "Send OTP"}
            </button>
          </form>
          )}

          {stage === "verify" && (
          <form onSubmit={handleVerify} className="space-y-6">
            <p className="text-slate-700">We sent a 6‑digit code to <span className="font-medium">{emailForVerify}</span>. Enter it below to verify your email.</p>
            <div>
              <label htmlFor="otp" className="block text-sm font-medium text-slate-900 mb-2">
                Verification code
              </label>
              <input
                id="otp"
                type="text"
                name="otp"
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent tracking-widest"
                placeholder="123456"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Verifying..." : "Verify & Continue to Sign In"}
            </button>

            <button
              type="button"
              onClick={() => setStage("form")}
              className="w-full px-4 py-2 mt-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50"
            >
              Back
            </button>
          </form>
          )}

          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
          <p className="mt-6 text-center text-sm text-slate-600">
            Already have an account?{" "}
            <Link href="/auth/signin" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
