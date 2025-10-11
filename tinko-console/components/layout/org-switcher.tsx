"use client";

import { useState } from "react";
import { Building2, Check, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useSession } from "@/lib/auth/client";

export function OrgSwitcher() {
  const { data, update } = useSession();
  const [activeOrg, setActiveOrg] = useState(data.activeOrganizationId);

  const handleSelect = (orgId: string) => {
    setActiveOrg(orgId);
    update(orgId);
  };

  const currentOrg = data.organizations.find((org) => org.id === activeOrg) ?? data.organizations[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="lg"
          className="inline-flex items-center gap-2 rounded-xl border-border/70 bg-white px-3 py-2 text-sm font-medium shadow-sm shadow-primary/10 hover:bg-secondary"
          aria-label="Select organization"
        >
          <Building2 className="h-4 w-4 text-primary" aria-hidden />
          <span className="max-w-[8rem] truncate text-left sm:max-w-xs">{currentOrg?.name}</span>
          <ChevronsUpDown className="h-4 w-4 text-muted-foreground" aria-hidden />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56 rounded-2xl border-border/70 bg-card/95 p-2 shadow-lg">
        <DropdownMenuLabel className="text-xs uppercase text-muted-foreground">
          Organizations
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {data.organizations.map((org) => (
          <DropdownMenuCheckboxItem
            key={org.id}
            checked={org.id === activeOrg}
            onCheckedChange={(checked) => checked && handleSelect(org.id)}
            className="rounded-lg text-sm"
          >
            <div className="flex w-full items-center justify-between gap-2">
              <span>{org.name}</span>
              {org.id === activeOrg ? <Check className="h-4 w-4 text-primary" aria-hidden /> : null}
            </div>
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
