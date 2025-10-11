import { CheckCircle2, Clock3, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { SectionCard } from "@/components/ui/section-card";
import { EmptyState } from "@/components/states/empty-state";

const checklist = [
  {
    title: "Connect merchant data sources",
    description: "Link payment gateway, POS, and ERP systems to sync outstanding balances.",
    status: "In progress",
    icon: Clock3,
  },
  {
    title: "Map customer identifiers",
    description: "Upload CSV or configure API mapping to match Tinko IDs with your finance data.",
    status: "Pending",
    icon: ShieldCheck,
  },
  {
    title: "Schedule recovery automations",
    description: "Define the cadence for outreach sequences and assign escalation owners.",
    status: "Pending",
    icon: CheckCircle2,
  },
];

export default function OnboardingPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Onboarding"
        description="Track readiness tasks that unlock automated recovery workflows across your merchant portfolio."
        action={<Button>View onboarding guide</Button>}
      />

      <SectionCard title="Implementation checklist" description="Mark items complete as your team progresses.">
        <div className="space-y-6">
          {checklist.map((item) => (
            <div
              key={item.title}
              className="flex flex-col gap-3 rounded-2xl border border-border/50 bg-white/80 p-4 shadow-sm sm:flex-row sm:items-center"
            >
              <div className="flex items-center gap-3 text-primary">
                <item.icon className="h-5 w-5" aria-hidden />
                <p className="text-sm font-semibold uppercase tracking-wide text-primary">{item.status}</p>
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-base font-medium text-foreground/90">{item.title}</p>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
              <Button variant="outline" size="sm" className="self-end sm:self-center">
                Mark complete
              </Button>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard
        title="Integrations status"
        description="As soon as your systems are linked, status updates and data sync logs will appear here."
      >
        <EmptyState
          title="No integrations connected"
          description="Add your first integration via the developer logs page to unlock automated data sync."
          action={<Button variant="outline">Go to developer logs</Button>}
        />
      </SectionCard>
    </div>
  );
}
