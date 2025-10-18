import Link from "next/link";
import SidebarNav from "./sidebar-nav";

export default function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Tinko
          </Link>
        </div>
        <SidebarNav />
        <div className="mt-auto p-6 border-t border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-sm font-medium text-blue-600">U</span>
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-900">User Account</p>
              <p className="text-slate-600">user@example.com</p>
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-slate-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Console</h2>
            <div className="flex items-center gap-4">
              <button className="text-sm text-slate-600 hover:text-slate-900">
                Settings
              </button>
              <button className="text-sm text-slate-600 hover:text-slate-900">
                Help
              </button>
            </div>
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
