import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { createHostel, deactivateHostel, listHostels } from '../api/hostels'
import { useAuth } from '../auth/AuthContext'

const emptyForm = {
  name: '',
  code: '',
  address: '',
  contact_name: '',
  phone: '',
  default_rate_per_liter: '',
}

export function HostelsPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState<string | null>(null)

  const hostelsQuery = useQuery({
    queryKey: ['hostels'],
    queryFn: ({ signal }) => listHostels(signal),
  })

  const createMutation = useMutation({
    mutationFn: createHostel,
    onSuccess: async () => {
      setForm(emptyForm)
      setFormError(null)
      await queryClient.invalidateQueries({ queryKey: ['hostels'] })
    },
    onError: (error: unknown) => {
      if (error instanceof ApiError) {
        const body = error.body as { error?: { message?: string } } | null
        setFormError(body?.error?.message ?? `Create failed (${error.status})`)
        return
      }
      setFormError('Could not create hostel')
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: deactivateHostel,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['hostels'] })
    },
  })

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    createMutation.mutate({
      name: form.name.trim(),
      code: form.code.trim(),
      address: form.address.trim() || null,
      contact_name: form.contact_name.trim() || null,
      phone: form.phone.trim() || null,
      default_rate_per_liter: form.default_rate_per_liter.trim(),
    })
  }

  const items = hostelsQuery.data?.items ?? []

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">
            rrvijayamilkagencies.com
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Hostels</h1>
          <p className="mt-2 text-slate-600">
            RR Vijaya Milk Agencies · signed in as {user?.email}
          </p>
        </div>
        <div className="flex gap-4">
          <Link
            to="/"
            className="text-sm font-medium text-emerald-800 underline-offset-4 hover:underline"
          >
            Status
          </Link>
          <button
            type="button"
            className="text-sm font-medium text-slate-700 underline-offset-4 hover:underline"
            onClick={async () => {
              await logout()
              navigate('/login', { replace: true })
            }}
          >
            Log out
          </button>
        </div>
      </div>

      <section className="mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Add hostel</h2>
        <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={onSubmit}>
          <label className="grid gap-1 text-sm text-slate-700">
            Name
            <input
              required
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.name}
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Code
            <input
              required
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.code}
              onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Rate per liter
            <input
              required
              type="number"
              min="0.01"
              step="0.01"
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.default_rate_per_liter}
              onChange={(event) =>
                setForm((current) => ({ ...current, default_rate_per_liter: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Contact name
            <input
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.contact_name}
              onChange={(event) =>
                setForm((current) => ({ ...current, contact_name: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Phone
            <input
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.phone}
              onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700 sm:col-span-2">
            Address
            <input
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={form.address}
              onChange={(event) => setForm((current) => ({ ...current, address: event.target.value }))}
            />
          </label>
          {formError && <p className="sm:col-span-2 text-sm text-red-600">{formError}</p>}
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {createMutation.isPending ? 'Saving…' : 'Save hostel'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Hostel list</h2>

        {hostelsQuery.isLoading && <p className="mt-4 text-slate-600">Loading hostels…</p>}
        {hostelsQuery.isError && (
          <p className="mt-4 text-red-600">Could not load hostels. Is the backend running?</p>
        )}
        {hostelsQuery.isSuccess && items.length === 0 && (
          <p className="mt-4 text-slate-600">No hostels yet. Add one above.</p>
        )}

        {items.length > 0 && (
          <ul className="mt-6 divide-y divide-slate-100">
            {items.map((hostel) => (
              <li key={hostel.id} className="flex flex-wrap items-center justify-between gap-3 py-4">
                <div>
                  <p className="font-semibold text-slate-900">
                    {hostel.name}{' '}
                    <span className="font-normal text-slate-500">({hostel.code})</span>
                  </p>
                  <p className="text-sm text-slate-600">
                    ₹{hostel.default_rate_per_liter}/L · {hostel.active ? 'Active' : 'Inactive'}
                  </p>
                </div>
                {hostel.active && (
                  <button
                    type="button"
                    className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                    disabled={deactivateMutation.isPending}
                    onClick={() => deactivateMutation.mutate(hostel.id)}
                  >
                    Deactivate
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}
