import Link from "next/link";

export default function RulesPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Recovery Rules</h1>
      
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Active Rules</h2>
        
        <div className="space-y-4">
          <div className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-slate-900">3-Day Follow-up</h3>
              <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">Active</span>
            </div>
            <p className="text-sm text-slate-600">Send follow-up email 3 days after failed payment</p>
          </div>
          
          <div className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-slate-900">7-Day Reminder</h3>
              <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">Active</span>
            </div>
            <p className="text-sm text-slate-600">Send reminder if payment still pending after 7 days</p>
          </div>
          
          <div className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-slate-900">Final Notice</h3>
              <span className="px-3 py-1 bg-amber-100 text-amber-700 text-sm rounded-full">Draft</span>
            </div>
            <p className="text-sm text-slate-600">Final notification before account suspension</p>
          </div>
        </div>
      </div>

      <Link href="/settings/retry" className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
        Edit Retry Policy
      </Link>
    </div>
  );
}
