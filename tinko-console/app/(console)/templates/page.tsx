import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { SectionCard } from "@/components/ui/section-card";
import { EmptyState } from "@/components/states/empty-state";

export default function TemplatesPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Templates"
        description="Save reusable outreach scripts and payment plan journeys for your merchant segments."
      />

      <SectionCard>
        <EmptyState
          title="Coming soon"
          description="Template management will let you author multi-channel flows and assign them to recovery rules."
          action={<Button disabled>Template builder under construction</Button>}
        />
      </SectionCard>
    </div>
  );
}
