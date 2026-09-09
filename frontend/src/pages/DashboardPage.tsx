import { useQuery } from '@tanstack/react-query'

import { getDashboard } from '../api/dashboard'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'

function KpiCard({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint: string
}) {
  return (
    <article className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5">
      <h2 className="text-sm font-medium text-slate-600">{label}</h2>
      <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{hint}</p>
    </article>
  )
}

export function DashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ['dashboard'],
    queryFn: ({ signal }) => getDashboard(signal),
    retry: false,
  })

  const data = dashboardQuery.data
  const isEmpty =
    dashboardQuery.isSuccess &&
    data !== undefined &&
    data.active_hostel_count === 0 &&
    Number(data.todays_supply) === 0 &&
    Number(data.revenue) === 0 &&
    Number(data.pending_payments) === 0

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
      <p className="mt-2 text-slate-600">
        Verified totals from PostgreSQL. Today uses the business timezone, not UTC.
      </p>

      {dashboardQuery.isLoading && <PageLoading message="Loading dashboard…" />}
      {dashboardQuery.isError && (
        <PageError message="Could not load dashboard totals. Is the backend running?" />
      )}

      {data && (
        <>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <KpiCard
              label="Active hostels"
              value={String(data.active_hostel_count)}
              hint="Hostels marked active"
            />
            <KpiCard
              label="Today's supply"
              value={`${data.todays_supply} L`}
              hint={`Deliveries dated ${data.as_of_date} (${data.timezone})`}
            />
            <KpiCard
              label="Revenue"
              value={`₹${data.revenue}`}
              hint={`Paid invoice totals for ${data.revenue_month}`}
            />
            <KpiCard
              label="Pending payments"
              value={`₹${data.pending_payments}`}
              hint="Remaining on unpaid, partial, and overdue invoices"
            />
          </div>
          {isEmpty && (
            <PageEmpty message="No billed activity yet. Add a hostel and a delivery to see totals move." />
          )}
        </>
      )}
    </div>
  )
}
