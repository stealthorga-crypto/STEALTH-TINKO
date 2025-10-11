import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { PageDescription } from "@/components/ui/page-description";
import { SectionCard } from "@/components/ui/section-card";
import { LoadingState } from "@/components/states/loading-state";
import { ErrorState } from "@/components/states/error-state";

export default function DeveloperLogsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Developer logs"
        description="Inspect webhook deliveries, API sync jobs, and automation executions to troubleshoot issues quickly."
        action={<Button variant="outline">Open API docs</Button>}
      >
        <PageDescription>
          Use this view to validate payloads, confirm retry logic, and export traces when integrating the Recovery API.
        </PageDescription>
      </PageHeader>

      <SectionCard
        title="Recent events"
        description="Hook up NEXT_PUBLIC_API_URL to stream logs via React Query."
        action={<Button size="sm">Refresh</Button>}
      >
        <LoadingState label="Fetching logs" />
      </SectionCard>

      <SectionCard
        title="Webhooks"
        description="Failed webhook deliveries will appear here once the API is connected."
      >
        <ErrorState
          title="No webhook endpoint configured"
          description="Set a webhook destination via the developer settings to receive recovery lifecycle events."
          action={<Button variant="outline">Configure endpoint</Button>}
        />
      </SectionCard>
    </div>
  );
}
