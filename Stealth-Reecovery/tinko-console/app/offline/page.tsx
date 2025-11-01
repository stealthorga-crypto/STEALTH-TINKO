"use client";

import Link from "next/link";
import { WifiOff, RefreshCw, Home } from "lucide-react";

export default function OfflinePage() {
  return (
    <div className="grid min-h-dvh place-items-center bg-gradient-to-br from-slate-50 via-white to-blue-50 px-4 py-10">
      <div className="w-full max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <div className="rounded-full bg-slate-100 p-6">
            <WifiOff className="h-16 w-16 text-slate-600" strokeWidth={1.5} />
          </div>
        </div>

        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          You&apos;re Offline
        </h1>
        
        <p className="text-lg text-slate-600 mb-2">
          No internet connection detected
        </p>
        
        <p className="text-sm text-slate-500 mb-8">
          Please check your network connection and try again. Some features may be available offline.
        </p>

        <div className="space-y-3">
          <button
            onClick={() => window.location.reload()}
            className="btn-primary w-full py-3 flex items-center justify-center gap-2"
          >
            <RefreshCw className="h-5 w-5" />
            Try Again
          </button>

          <Link
            href="/"
            className="btn-secondary w-full py-3 flex items-center justify-center gap-2"
          >
            <Home className="h-5 w-5" />
            Go to Homepage
          </Link>
        </div>

        <div className="mt-12 p-4 bg-blue-50 border border-blue-200 rounded-xl text-left">
          <h3 className="font-semibold text-blue-900 mb-2">
            💡 Offline Features
          </h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• View previously loaded pages</li>
            <li>• Access cached dashboard data</li>
            <li>• Browse documentation</li>
          </ul>
          <p className="text-xs text-blue-600 mt-2">
            Changes will sync when you&apos;re back online.
          </p>
        </div>

        <p className="mt-8 text-xs text-slate-500">
          Need help? <Link href="/contact" className="text-primary-600 hover:text-primary-700 font-medium">Contact Support</Link>
        </p>
      </div>
    </div>
  );
}
