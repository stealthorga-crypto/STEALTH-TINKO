import Link from "next/link";
import { AlertCircle } from "lucide-react";

interface AuthErrorPageProps {
  searchParams: Promise<{
    error?: string;
  }>;
}

const errorMessages: Record<string, string> = {
  Configuration: "There is a problem with the server configuration. Please contact support.",
  AccessDenied: "You do not have permission to sign in.",
  Verification: "The verification token has expired or has already been used.",
  OAuthSignin: "Error occurred during sign in with OAuth provider.",
  OAuthCallback: "Error occurred during OAuth callback.",
  OAuthCreateAccount: "Could not create OAuth provider user in the database.",
  EmailCreateAccount: "Could not create email provider user in the database.",
  Callback: "Error occurred during callback.",
  OAuthAccountNotLinked: "This account is already linked to another user.",
  EmailSignin: "Check your email for the sign-in link.",
  CredentialsSignin: "Sign in failed. Check your credentials and try again.",
  SessionRequired: "Please sign in to access this page.",
  Default: "Unable to sign in. Please try again.",
};

export default async function AuthErrorPage({ searchParams }: AuthErrorPageProps) {
  const params = await searchParams;
  const error = params.error || "Default";
  const errorMessage = errorMessages[error] || errorMessages.Default;

  return (
    <div className="grid min-h-dvh place-items-center bg-gradient-to-br from-primary-50 via-white to-blue-50 px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-strong">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary-600 text-white font-bold text-lg shadow-md">
            T
          </div>
          <div className="text-xl font-bold text-slate-900">Tinko Recovery</div>
        </div>

        <div className="flex items-start gap-3 mb-6">
          <div className="rounded-full bg-error-100 p-2">
            <AlertCircle className="h-6 w-6 text-error-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Authentication Error</h1>
            <p className="mt-2 text-slate-600">{errorMessage}</p>
            {error !== "Default" && (
              <p className="mt-2 text-xs text-slate-500 font-mono bg-slate-50 px-2 py-1 rounded">
                Error code: {error}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <Link
            href="/auth/signin"
            className="btn-primary w-full py-3 text-center"
          >
            Try Again
          </Link>
          <Link
            href="/"
            className="btn-secondary w-full py-3 text-center"
          >
            Return to Home
          </Link>
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          Need help?{" "}
          <Link href="/contact" className="text-primary-600 hover:text-primary-700">
            Contact support
          </Link>
        </p>
      </div>
    </div>
  );
}
