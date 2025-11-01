"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useSession } from "@/lib/auth/client";
import { LogOut, Settings, UserRound } from "lucide-react";

const initials = (name: string) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase();

export function UserMenu() {
  const { data } = useSession();
  const { user } = data;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-3 rounded-full px-2 py-1 text-left hover:bg-secondary"
          aria-label="Open user menu"
        >
          <Avatar className="h-9 w-9 border border-border/50">
            <AvatarImage src={user.image} alt={user.name} />
            <AvatarFallback>{initials(user.name)}</AvatarFallback>
          </Avatar>
          <div className="hidden text-left sm:block">
            <p className="text-sm font-semibold text-foreground/90">{user.name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56 rounded-2xl border-border/70 bg-card/95 p-2 shadow-lg" align="end">
        <DropdownMenuLabel className="text-xs uppercase text-muted-foreground">
          Account
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem className="rounded-lg text-sm">
            <UserRound className="mr-2 h-4 w-4 text-muted-foreground" aria-hidden />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem className="rounded-lg text-sm">
            <Settings className="mr-2 h-4 w-4 text-muted-foreground" aria-hidden />
            Preferences
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="rounded-lg text-sm text-destructive">
          <LogOut className="mr-2 h-4 w-4" aria-hidden />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
