"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function SigninPage() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const form = new FormData(e.currentTarget);
    const email = String(form.get("email") || "");
    const password = String(form.get("password") || "");
    try {
      const res = await api.post<{ access_token: string; user: any; organization: any }>(
        "/v1/auth/login",
        { email, password }
      );
      const token = (res as any)?.access_token;
      if (token) {
        // Store token in localStorage and cookie for middleware
        if (typeof window !== "undefined") {
          window.localStorage.setItem("auth_token", token);
          document.cookie = `authjs.session-token=${encodeURIComponent(token)}; path=/; samesite=lax`;
          if ((res as any).organization?.name) {
            window.localStorage.setItem("org_name", (res as any).organization.name);
          }
          if ((res as any).user?.email) {
            window.localStorage.setItem("user_email", (res as any).user.email);
          }
        }
        const cb = params.get("callbackUrl") || "/dashboard";
        router.push(cb);
        return;
      }
      setError("Login failed");
    } catch (e) {
      setError("Incorrect email or password");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            Tinko
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 mt-4">Welcome back</h1>
          <p className="text-slate-600 mt-2">Sign in to your account</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-900 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                name="email"
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
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4 text-blue-600 border-slate-300 rounded" />
                <span className="ml-2 text-sm text-slate-600">Remember me</span>
              </label>
              <Link href="/auth/forgot-password" className="text-sm text-blue-600 hover:text-blue-700">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign In
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-600">
            Don&apos;t have an account?{" "}
            <Link href="/auth/signup" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
