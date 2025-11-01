"use client";

import { useEffect } from "react";
import { ErrorState } from "@/components/states/error-state";
import { Button } from "@/components/ui/button";

export default function ConsoleError({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="space-y-4 p-8">
      <ErrorState
        title="We hit a snag"
        description="An unexpected error occurred while loading the console. Try again or contact support if this persists."
        action={
          <Button onClick={reset} variant="outline">
            Retry
          </Button>
        }
      />
    </div>
  );
}
