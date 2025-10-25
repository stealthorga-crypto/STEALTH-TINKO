"use client";

import type { RetryPolicy } from "@/lib/retryPolicies";

export function PolicyList({
  items,
  onDelete,
  activeId,
  onRefresh,
}: {
  items: RetryPolicy[];
  onDelete: (id: number) => Promise<void> | void;
  activeId?: number | null;
  onRefresh?: () => Promise<void> | void;
}) {
  if (!items?.length) {
    return <div className="text-sm text-slate-500">No policies yet. Create one to get started.</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border border-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-3 py-2 text-left text-sm font-semibold text-slate-700">Name</th>
            <th className="px-3 py-2 text-left text-sm font-semibold text-slate-700">Retries</th>
            <th className="px-3 py-2 text-left text-sm font-semibold text-slate-700">Delays (min)</th>
            <th className="px-3 py-2 text-left text-sm font-semibold text-slate-700">Channels</th>
            <th className="px-3 py-2 text-right text-sm font-semibold text-slate-700">
              <div className="flex items-center justify-end gap-2">
                <span>Actions</span>
                {onRefresh && (
                  <button
                    className="rounded border border-slate-300 bg-white px-2 py-1 text-xs text-slate-700 hover:bg-slate-50"
                    onClick={() => onRefresh?.()}
                  >
                    Refresh
                  </button>
                )}
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id} className="border-t">
              <td className="px-3 py-2 text-sm">
                <div className="flex items-center gap-2">
                  <span>{p.name}</span>
                  {p.is_active || (activeId != null && activeId === p.id) ? (
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">Active</span>
                  ) : null}
                </div>
              </td>
              <td className="px-3 py-2 text-sm">{p.max_retries}</td>
              <td className="px-3 py-2 text-sm">
                init {p.initial_delay_minutes}, backoff x{p.backoff_multiplier}, max {p.max_delay_minutes}
              </td>
              <td className="px-3 py-2 text-sm">{p.enabled_channels?.join(", ") || "-"}</td>
              <td className="px-3 py-2 text-right">
                <button
                  className="rounded bg-rose-600 px-3 py-1 text-sm text-white hover:bg-rose-700"
                  onClick={() => onDelete(p.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
