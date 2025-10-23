"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const form = new FormData(e.currentTarget);
    const full_name = String(form.get("name") || "");
    const email = String(form.get("email") || "");
    const password = String(form.get("password") || "");
    const org_name = String(form.get("org") || "");
    try {
      const res = await api.post<{ access_token: string; user: any; organization: any }>(
        "/v1/auth/register",
        { full_name, email, password, org_name }
      );
      const token = (res as any)?.access_token;
      if (token) {
        if (typeof window !== "undefined") {
          window.localStorage.setItem("auth_token", token);
          document.cookie = `authjs.session-token=${encodeURIComponent(token)}; path=/; samesite=lax`;
          if ((res as any).organization?.name) {
            window.localStorage.setItem("org_name", (res as any).organization.name);
          }
          if ((res as any).user?.email) {
            window.localStorage.setItem("user_email", (res as any).user.email);
          }
          if ((res as any).user?.role) {
            window.localStorage.setItem("user_role", (res as any).user.role);
          }
        }
        router.push("/onboarding");
        return;
      }
      setError("Registration failed");
    } catch (e) {
      setError("Failed to register. Check details and try again.");
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
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-900 mb-2">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                name="name"
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

            <div>
              <label htmlFor="org" className="block text-sm font-medium text-slate-900 mb-2">
                Organization Name
              </label>
              <input
                id="org"
                type="text"
                name="org"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                placeholder="Acme Inc."
              />
            </div>

            <button
              type="submit"
              className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Account
            </button>
          </form>

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
