export default function PaymentSuccessPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center space-y-2">
        <h1 className="text-2xl font-semibold text-slate-900">Payment complete</h1>
        <p className="text-slate-700">Thank you! You can close this window.</p>
      </div>
    </div>
  );
}
