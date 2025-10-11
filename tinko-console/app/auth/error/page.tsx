import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/states/error-state";

export default function AuthErrorPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary/10 via-white to-secondary/50 p-6">
      <div className="w-full max-w-lg">
        <ErrorState
          title="Authentication error"
          description="We could not sign you in. This placeholder page will surface NextAuth error messages in a future update."
          action={
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button asChild>
                <Link href="/auth/signin">Try again</Link>
              </Button>
              <Button asChild variant="outline">
                <Link href="/dashboard">Return to console</Link>
              </Button>
            </div>
          }
        />
      </div>
    </div>
  );
}
