// app/pay/[token]/page.tsx
'use client';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { CreditCard, AlertCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';

interface RecoveryAttempt {
  id: number;
  transaction_ref: string;
  channel: string;
  status: string;
  expires_at: string;
  payment_link_url?: string;
}

export default function PaymentRecoveryPage() {
  const params = useParams();
  const token = params.token as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recovery, setRecovery] = useState<RecoveryAttempt | null>(null);
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    if (token) {
      fetchRecoveryAttempt(token);
    }
  }, [token]);

  const fetchRecoveryAttempt = async (token: string) => {
    try {
      const response = await fetch(`http://localhost:8000/v1/recoveries/by_token/${token}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('Recovery link not found or has expired');
        } else {
          setError('Failed to load payment information');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setRecovery(data);

      // Mark as opened
      await fetch(`http://localhost:8000/v1/recoveries/by_token/${token}/open`, {
        method: 'POST',
      });

      // If payment link available, redirect after showing info
      if (data.payment_link_url) {
        setRedirecting(true);
        setTimeout(() => {
          window.location.href = data.payment_link_url;
        }, 3000);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error fetching recovery:', err);
      setError('Failed to load payment information');
      setLoading(false);
    }
  };

  const handlePayNow = () => {
    if (recovery?.payment_link_url) {
      window.location.href = recovery.payment_link_url;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading payment information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="bg-red-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">
            Payment Link Invalid
          </h1>
          <p className="text-slate-600 mb-6">{error}</p>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  if (recovery?.status === 'completed') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="bg-green-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <CreditCard className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">
            Already Paid
          </h1>
          <p className="text-slate-600 mb-6">
            This payment has already been completed. Thank you!
          </p>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="bg-blue-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <CreditCard className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">
            Complete Your Payment
          </h1>
          <p className="text-slate-600">
            We noticed your recent payment couldn&apos;t be completed.
          </p>
        </div>

        {/* Payment Details */}
        <div className="bg-slate-50 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-slate-900 mb-3">Payment Details</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-600">Transaction</span>
              <span className="font-mono text-slate-900">{recovery?.transaction_ref}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Status</span>
              <span className="font-semibold text-orange-600 capitalize">{recovery?.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Expires</span>
              <span className="text-slate-900">
                {recovery?.expires_at && new Date(recovery.expires_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Redirecting Message */}
        {redirecting && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
            <p className="text-sm text-blue-800">
              Redirecting you to secure payment page...
            </p>
          </div>
        )}

        {/* Action Button */}
        {recovery?.payment_link_url && !redirecting && (
          <button
            onClick={handlePayNow}
            className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 mb-4"
          >
            <CreditCard className="w-5 h-5" />
            Pay Now
          </button>
        )}

        {/* Security Note */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-semibold text-green-900 text-sm mb-1">
            🔒 Secure Payment
          </h4>
          <p className="text-xs text-green-800">
            Your payment is processed securely through Stripe. We never store your card details.
          </p>
        </div>

        {/* Support Link */}
        <p className="text-center text-sm text-slate-500 mt-6">
          Questions? <Link href="/contact" className="text-blue-600 hover:underline">Contact Support</Link>
        </p>
      </div>
    </div>
  );
}

