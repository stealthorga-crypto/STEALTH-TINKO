export default function DeveloperPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Developer Tools</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">API Keys</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-2">Production API Key</label>
              <div className="flex gap-2">
                <input 
                  type="password" 
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg font-mono text-sm" 
                  defaultValue="sk_live_abc123xyz789"
                  readOnly
                />
                <button className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50">
                  Copy
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-2">Test API Key</label>
              <div className="flex gap-2">
                <input 
                  type="password" 
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg font-mono text-sm" 
                  defaultValue="sk_test_def456uvw012"
                  readOnly
                />
                <button className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50">
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Webhooks</h2>
          <p className="text-sm text-slate-600 mb-4">Configure webhook endpoints for real-time events</p>
          <button className="px-6 py-3 border border-slate-300 rounded-lg hover:bg-slate-50">
            Add Webhook
          </button>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">API Documentation</h2>
          <p className="text-sm text-slate-600 mb-4">View our comprehensive API documentation</p>
          <a href="https://docs.tinko.in" target="_blank" rel="noopener noreferrer" className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
            View Docs
          </a>
        </div>
      </div>
    </div>
  );
}
