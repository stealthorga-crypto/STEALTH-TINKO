"use client";

import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { Fragment } from "react";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/states/loading-state";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { api } from "@/lib/api";

const mockEvents = [
  {
    id: "evt_mock_1",
    merchant: "Blue Finch Retail",
    action: "Invoice auto-collected",
    amount: "$1,240.00",
    occurredAt: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
  },
  {
    id: "evt_mock_2",
    merchant: "Central Outfitters",
    action: "Escalation triggered",
    amount: "$620.00",
    occurredAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
  },
  {
    id: "evt_mock_3",
    merchant: "Sunrise Goods",
    action: "Promise to pay scheduled",
    amount: "$480.00",
    occurredAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
  },
];

type RecoveryEvent = (typeof mockEvents)[number];

const fetchRecoveryEvents = async (): Promise<RecoveryEvent[]> => {
  if (!process.env.NEXT_PUBLIC_API_URL) {
    return mockEvents;
  }

  try {
    return await api.get<RecoveryEvent[]>("/recovery/events");
  } catch (error) {
    console.warn("Falling back to mock recovery events", error);
    return mockEvents;
  }
};

export function RecoveryFeed() {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["recovery-feed"],
    queryFn: fetchRecoveryEvents,
    staleTime: 60_000,
  });

  if (isLoading) {
    return <LoadingState label="Loading recovery activity" />;
  }

  if (isError) {
    return (
      <ErrorState
        title="Unable to load activity"
        description="We could not reach the Recovery API. Check NEXT_PUBLIC_API_URL or try again."
        action={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        }
      />
    );
  }

  if (!data?.length) {
    return (
      <EmptyState
        title="No recent activity"
        description="Once merchants are connected, recovery events will start populating in real time."
        action={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Refresh
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      {data.map((event, index) => (
        <Fragment key={event.id}>
          <div className="flex flex-col gap-2 rounded-2xl border border-border/60 bg-white/80 p-4 shadow-sm sm:flex-row sm:items-center">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground/90">{event.action}</p>
              <p className="text-sm text-muted-foreground">
                {event.merchant} - {event.amount}
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              {formatDistanceToNow(new Date(event.occurredAt), { addSuffix: true })}
            </p>
          </div>
          {index < data.length - 1 ? <div className="h-px bg-border/70" aria-hidden /> : null}
        </Fragment>
      ))}
      <div className="flex items-center justify-end">
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? "Refreshing..." : "Refresh"}
        </Button>
      </div>
    </div>
  );
}
