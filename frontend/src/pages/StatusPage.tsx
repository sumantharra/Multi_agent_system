import { useQuery } from '@tanstack/react-query'

import { getHealth } from '../api/health'

export function StatusPage() {
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => getHealth(signal),
    retry: false,
  })

  const connected = healthQuery.isSuccess && healthQuery.data.status === 'ok'

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-xl rounded-3xl border border-emerald-100 bg-white p-8 shadow-xl shadow-emerald-950/5 sm:p-12">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
          Multi-Agent Platform
        </p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          Foundation status
        </h1>
        <p className="mt-4 leading-7 text-slate-600">
          Phase 1 verifies that the browser application can communicate with the API.
        </p>

        <div
          className="mt-8 flex items-center gap-4 rounded-2xl bg-slate-50 p-5"
          role="status"
          aria-live="polite"
        >
          <span
            className={`h-3 w-3 shrink-0 rounded-full ${
              connected
                ? 'bg-emerald-500'
                : healthQuery.isError
                  ? 'bg-red-500'
                  : 'animate-pulse bg-amber-400'
            }`}
          />
          <div>
            <p className="font-semibold text-slate-900">
              {connected
                ? 'Backend connected'
                : healthQuery.isError
                  ? 'Backend unavailable'
                  : 'Checking backend connection…'}
            </p>
            {connected && (
              <p className="mt-1 text-sm text-slate-500">
                {healthQuery.data.service} · {healthQuery.data.environment}
              </p>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}
