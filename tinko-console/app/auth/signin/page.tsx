import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-secondary/60 via-white to-primary/10 p-6">
      <div className="w-full max-w-md rounded-3xl border border-border/60 bg-white/95 p-8 shadow-2xl shadow-primary/10 backdrop-blur">
        <div className="mb-6 space-y-2 text-center">
          <p className="text-xs uppercase tracking-wide text-primary">Tinko Recovery Console</p>
          <h1 className="text-2xl font-semibold text-foreground/90">Sign in to continue</h1>
          <p className="text-sm text-muted-foreground">
            Use the credentials issued by Tinko. SSO providers will be available in the next milestone.
          </p>
        </div>
        <form className="space-y-4">
          <label className="block text-sm font-medium text-foreground/80" htmlFor="email">
            Work email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            placeholder="you@company.com"
            className="w-full rounded-xl border border-border/70 bg-white px-4 py-3 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
          <label className="block pt-2 text-sm font-medium text-foreground/80" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            className="w-full rounded-xl border border-border/70 bg-white px-4 py-3 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
          <div className="flex items-center justify-between pt-1 text-sm">
            <label className="flex items-center gap-2 text-muted-foreground">
              <input type="checkbox" className="h-4 w-4 rounded border-border/70 text-primary focus:ring-primary" />
              Remember me
            </label>
            <Link href="/auth/error" className="font-medium text-primary hover:underline">
              Trouble signing in?
            "use client";

            "use client";

            import { signIn } from "next-auth/react";
            import { useState } from "react";

            export default function SignIn() {
              const [email, setEmail] = useState("");
              const [password, setPassword] = useState("");
              const [busy, setBusy] = useState(false);

              async function onSubmit(e: React.FormEvent) {
                e.preventDefault();
                setBusy(true);
                const res = await signIn("credentials", { redirect: false, email, password });
                setBusy(false);
                if (res?.ok) window.location.href = "/dashboard";
                else alert(res?.error ?? "Sign-in failed");
              }

              return (
                <div className="grid min-h-dvh place-items-center bg-slate-50 px-4 py-10">
                  <div className="w-full max-w-sm rounded-2xl border bg-white p-6 shadow-sm">
                    <div className="mb-5 flex items-center gap-2">
                      <div className="grid h-8 w-8 place-items-center rounded-xl bg-blue-600 text-white font-semibold">T</div>
                      <div className="text-sm font-semibold">Tinko</div>
                    </div>
                    <h1 className="text-lg font-medium">Welcome back</h1>
                    <p className="mt-1 text-sm text-slate-600">Sign in to your merchant console.</p>

                    <form onSubmit={onSubmit} className="mt-4 space-y-3">
                      <label className="block text-xs text-slate-600">Email</label>
                      <input
                        className="w-full rounded-xl border px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                        type="email" placeholder="you@company.com" value={email} onChange={(e) => setEmail(e.target.value)} required
                      />
                      <label className="mt-3 block text-xs text-slate-600">Password</label>
                      <input
                        className="w-full rounded-xl border px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                        type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required
                      />
                      <button type="submit" disabled={busy} className="mt-4 w-full rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60">
                        {busy ? "Signing in…" : "Sign in"}
                      </button>
                    </form>

                    <p className="mt-4 text-center text-xs text-slate-500">
                      By continuing you agree to the Terms and Privacy Policy.
                    </p>
                  </div>
                </div>
              );
            }
