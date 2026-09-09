import { StatusPage } from './StatusPage'

export function DashboardPage() {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
      <p className="mt-2 text-slate-600">
        KPI cards come later. System status is below so you can confirm the API is reachable.
      </p>
      <div className="mt-8">
        <StatusPage />
      </div>
    </div>
  )
}
