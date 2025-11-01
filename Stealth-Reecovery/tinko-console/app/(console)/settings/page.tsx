export default function SettingsPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Settings</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Account Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-2">Company Name</label>
              <input type="text" className="w-full px-4 py-2 border border-slate-300 rounded-lg" defaultValue="Your Company" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-2">Email</label>
              <input type="email" className="w-full px-4 py-2 border border-slate-300 rounded-lg" defaultValue="admin@company.com" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Notifications</h2>
          <div className="space-y-3">
            <label className="flex items-center">
              <input type="checkbox" className="w-4 h-4 text-blue-600 border-slate-300 rounded" defaultChecked />
              <span className="ml-2 text-sm text-slate-700">Email notifications</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="w-4 h-4 text-blue-600 border-slate-300 rounded" defaultChecked />
              <span className="ml-2 text-sm text-slate-700">Recovery alerts</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="w-4 h-4 text-blue-600 border-slate-300 rounded" />
              <span className="ml-2 text-sm text-slate-700">Weekly reports</span>
            </label>
          </div>
        </div>

        <button className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700">
          Save Changes
        </button>
      </div>
    </div>
  );
}
