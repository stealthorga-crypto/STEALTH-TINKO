// app/pay/cancel/page.tsx
'use client';

import Link from 'next/link';
import { XCircle, ArrowLeft, RefreshCw } from 'lucide-react';

export default function PaymentCancelPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Cancel Icon */}
        <div className="flex justify-center mb-6">
          <div className="bg-orange-100 rounded-full p-3">
            <XCircle className="w-16 h-16 text-orange-600" />
          </div>
        </div>

        {/* Cancel Message */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Payment Cancelled
          </h1>
          <p className="text-slate-600">
            Your payment was cancelled. No charges were made to your account.
          </p>
        </div>

        {/* Information Box */}
        <div className="bg-slate-50 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-slate-900 mb-3">Why was this cancelled?</h3>
          <ul className="text-sm text-slate-600 space-y-2">
            <li>• You chose to cancel the payment</li>
            <li>• The payment window expired</li>
            <li>• There was an issue with your payment method</li>
          </ul>
        </div>

        {/* What to Do Next */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">What you can do:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Try again with a different payment method</li>
            <li>• Check your payment details</li>
            <li>• Contact support if you need assistance</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="grid gap-3">
          <button
            onClick={() => window.history.back()}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          
          <Link
            href="/"
            className="flex items-center justify-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Home
          </Link>
        </div>

        {/* Support Link */}
        <p className="text-center text-sm text-slate-500 mt-6">
          Having trouble? <Link href="/contact" className="text-blue-600 hover:underline">Contact Support</Link>
        </p>
      </div>
    </div>
  );
}
