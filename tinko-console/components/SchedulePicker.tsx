"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Slot = { start: string; end: string; score: number };

export function SchedulePicker({ refId, onSelect }: { refId: string; onSelect: (ts: string) => void }) {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const data = await api.get<{ ref: string; slots: Slot[] }>(
          `/v1/schedule/suggested_windows?ref=${encodeURIComponent(refId)}&hours_ahead=24`
        );
        setSlots(data?.slots ?? []);
      } catch (e) {
        console.error(e);
        setError("Failed to load suggested windows");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [refId]);

  if (loading) return <div className="text-sm text-slate-600">Loading suggestions…</div>;
  if (error) return <div className="text-sm text-red-600">{error}</div>;

  if (!slots.length) return <div className="text-sm text-slate-600">No suggestions available.</div>;

  return (
    <div className="grid grid-cols-2 gap-2">
      {slots.slice(0, 8).map((s) => (
        <button
          key={s.start}
          onClick={() => onSelect(s.start)}
          className="border rounded-md p-2 text-left hover:bg-slate-50"
        >
          <div className="text-sm font-medium text-slate-900">
            {new Date(s.start).toLocaleString()} – {new Date(s.end).toLocaleTimeString()}
          </div>
          <div className="text-xs text-slate-500">Score: {s.score}</div>
        </button>
      ))}
    </div>
  );
}
