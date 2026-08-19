import { Link, Navigate, Route, Routes } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { HostelsPage } from '../pages/HostelsPage'
import { LoginPage } from '../pages/LoginPage'
import { StatusPage } from '../pages/StatusPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center text-slate-600">
        Checking session…
      </main>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  return children
}

function StatusWithNav() {
  return (
    <div>
      <div className="flex justify-end gap-4 px-6 pt-6">
        <Link
          to="/hostels"
          className="text-sm font-medium text-emerald-800 underline-offset-4 hover:underline"
        >
          Hostels
        </Link>
        <Link
          to="/login"
          className="text-sm font-medium text-emerald-800 underline-offset-4 hover:underline"
        >
          Login
        </Link>
      </div>
      <StatusPage />
    </div>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<StatusWithNav />} />
      <Route
        path="/hostels"
        element={
          <RequireAuth>
            <HostelsPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
