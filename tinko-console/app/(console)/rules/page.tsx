import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { SectionCard } from "@/components/ui/section-card";
import { LoadingState } from "@/components/states/loading-state";
import { EmptyState } from "@/components/states/empty-state";

const ruleCategories = [
  {
    name: "High-risk merchants",
    description: "Escalate accounts with chargeback risk above threshold for manual review.",
  },
  {
    name: "Installment reminders",
    description: "Send multi-channel nudges for upcoming installment payments due within 3 days.",
  },
  {
    name: "Subscription recovery",
    description: "Retry failed renewals using smart retriage windows per payment processor.",
  },
];

export default function RulesPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Rules"
        description="Define the automation logic that powers your recovery workflows across merchant segments."
        action={<Button>Create rule</Button>}
      />

      <SectionCard
        title="Active rulesets"
        description="Connect the API or upload JSON configurations to populate this list."
        action={
          <Button variant="outline" size="sm">
            Import rules JSON
          </Button>
        }
      >
        <LoadingState label="Loading rules" />
      </SectionCard>

      <SectionCard title="Starter recipes" description="Tweak these blueprints to match your merchant programs.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {ruleCategories.map((category) => (
            <div key={category.name} className="rounded-2xl border border-border/60 bg-white/80 p-4 shadow-sm">
              <h3 className="text-base font-semibold text-foreground/90">{category.name}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{category.description}</p>
              <Button variant="ghost" size="sm" className="mt-3 px-0 text-primary">
                View draft
              </Button>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard>
        <EmptyState
          title="Next steps"
          description="Connect the recovery-rules endpoint and push your first strategy to activate automations."
          action={<Button variant="outline">Open developer docs</Button>}
        />
      </SectionCard>
    </div>
  );
}
