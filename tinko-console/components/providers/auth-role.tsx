"use client";

import { ReactNode } from "react";
import { useSession } from "../../lib/auth/client";

export function RequireRole({ role, children }: { role: string; children: ReactNode }) {
  const { data } = useSession();
  const currentRole = data?.role ?? "admin";
  if (currentRole !== role) {
    return (
      <div className="p-8 text-center text-slate-700">
        You do not have permission to view this page.
      </div>
    );
  }
  return <>{children}</>;
}
