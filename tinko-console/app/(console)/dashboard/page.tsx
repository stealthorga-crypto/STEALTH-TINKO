export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Total Recovered</p>
          <p className="text-3xl font-bold text-blue-600">$82.4K</p>
          <p className="text-xs text-green-600 mt-2">↑ 12% from last month</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Active Rules</p>
          <p className="text-3xl font-bold text-slate-900">18</p>
          <p className="text-xs text-slate-600 mt-2">3 templates applied</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Alerts</p>
          <p className="text-3xl font-bold text-amber-600">3</p>
          <p className="text-xs text-slate-600 mt-2">Requires attention</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Merchants</p>
          <p className="text-3xl font-bold text-slate-900">12</p>
          <p className="text-xs text-slate-600 mt-2">2 onboarding</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-slate-900">Payment recovered</p>
                <p className="text-xs text-slate-600">Merchant ABC - $450.00</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-slate-900">New rule applied</p>
                <p className="text-xs text-slate-600">3-day follow-up template</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-amber-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-slate-900">Alert triggered</p>
                <p className="text-xs text-slate-600">High failure rate detected</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Next Steps</h2>
          <ul className="space-y-2">
            <li className="flex items-center gap-2 text-sm text-slate-700">
              <span className="text-blue-600">→</span>
              Review pending recovery attempts
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-700">
              <span className="text-blue-600">→</span>
              Configure email templates
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-700">
              <span className="text-blue-600">→</span>
              Set up webhook notifications
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
