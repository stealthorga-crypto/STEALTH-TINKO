export default function TemplatesPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Email Templates</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Payment Reminder</h3>
          <p className="text-sm text-slate-600 mb-4">Friendly reminder for failed payment</p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Used 24 times</span>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">Edit</button>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Card Update Request</h3>
          <p className="text-sm text-slate-600 mb-4">Request to update payment method</p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Used 18 times</span>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">Edit</button>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Final Notice</h3>
          <p className="text-sm text-slate-600 mb-4">Last attempt before suspension</p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Used 5 times</span>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">Edit</button>
          </div>
        </div>
      </div>

      <button className="mt-6 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
        Create New Template
      </button>
    </div>
  );
}
