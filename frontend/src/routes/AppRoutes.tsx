import { Navigate, Route, Routes } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { AppShell } from '../components/layout/AppShell'
import { DeliveriesPage } from '../pages/DeliveriesPage'
import { DashboardPage } from '../pages/DashboardPage'
import { HostelsPage } from '../pages/HostelsPage'
import { InvoicesPage } from '../pages/InvoicesPage'
import { LoginPage } from '../pages/LoginPage'
import { PaymentsPage } from '../pages/PaymentsPage'

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

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/hostels" element={<HostelsPage />} />
        <Route path="/deliveries" element={<DeliveriesPage />} />
        <Route path="/invoices" element={<InvoicesPage />} />
        <Route path="/payments" element={<PaymentsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
