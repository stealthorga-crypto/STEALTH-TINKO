import Link from "next/link";

export default function GuestPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Guest Access</h1>
        <p className="text-lg text-slate-600 mb-8">
          Explore our platform with limited access
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
        >
          Continue to Dashboard
        </Link>
      </div>
    </div>
  );
}
