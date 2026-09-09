import { Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '../../auth/AuthContext'
import { Sidebar } from './Sidebar'

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function onLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(circle_at_top,_#e8f5ef,_#f4f8f6_45%,_#eef2f0)] md:flex-row">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-emerald-100 bg-white/80 px-6 py-4 backdrop-blur">
          <p className="text-sm text-slate-600">
            Signed in as <span className="font-medium text-slate-900">{user?.email}</span>
          </p>
          <button
            type="button"
            className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            onClick={() => void onLogout()}
          >
            Log out
          </button>
        </header>
        <div className="flex-1 px-6 py-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
