'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle, ArrowLeft, Download } from 'lucide-react';

export default function PaymentSuccessContent() {
  const searchParams = useSearchParams();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionData, setSessionData] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    const session_id = searchParams.get('session_id');
    setSessionId(session_id);

    if (session_id) {
      fetchSessionDetails(session_id);
    } else {
      setLoading(false);
    }
  }, [searchParams]);

  const fetchSessionDetails = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/v1/stripe/checkout/session/${sessionId}`);
      
      if (response.ok) {
        const data = await response.json();
        setSessionData(data);
      }
    } catch (error) {
      console.error('Failed to fetch session details:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </div>

        {/* Success Message */}
        <h1 className="text-3xl font-bold text-center text-slate-900 mb-2">
          Payment Successful!
        </h1>
        <p className="text-center text-slate-600 mb-8">
          Thank you for completing your payment.
        </p>

        {/* Payment Details */}
        {loading ? (
          <div className="bg-slate-50 rounded-lg p-6 mb-6 animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-3/4 mb-3"></div>
            <div className="h-4 bg-slate-200 rounded w-1/2"></div>
          </div>
        ) : sessionData ? (
          <div className="bg-slate-50 rounded-lg p-6 mb-6 space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Status</span>
              <span className="font-semibold text-green-600">
                {sessionData.payment_status || 'Paid'}
              </span>
            </div>
            {sessionData.amount_total && (
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">Amount</span>
                <span className="font-semibold text-slate-900">
                  {((sessionData.amount_total as number) / 100).toFixed(2)} {((sessionData.currency as string) || 'USD').toUpperCase()}
                </span>
              </div>
            )}
            {sessionData.customer_email && (
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">Email</span>
                <span className="font-semibold text-slate-900">
                  {sessionData.customer_email}
                </span>
              </div>
            )}
          </div>
        ) : sessionId ? (
          <div className="bg-slate-50 rounded-lg p-6 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Session ID</span>
              <span className="font-mono text-xs text-slate-500">{sessionId}</span>
            </div>
          </div>
        ) : null}

        {/* What's Next */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• You&apos;ll receive a confirmation email shortly</li>
            <li>• Your payment will be reflected in your account</li>
            <li>• No further action is required</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="grid gap-3">
          <button
            onClick={() => window.print()}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            Download Receipt
          </button>
          
          <Link
            href="/"
            className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Home
          </Link>
        </div>

        {/* Support Link */}
        <p className="text-center text-sm text-slate-500 mt-6">
          Need help? <a href="/support" className="text-blue-600 hover:underline">Contact Support</a>
        </p>
      </div>
    </div>
  );
}
