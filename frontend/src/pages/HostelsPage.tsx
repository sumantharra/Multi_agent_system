import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createHostel, deactivateHostel, listHostels, updateHostel } from '../api/hostels'
import { apiErrorMessage } from '../api/errors'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'
import type { Hostel } from '../types/hostel'

const emptyForm = {
  name: '',
  code: '',
  address: '',
  contact_name: '',
  phone: '',
  default_rate_per_liter: '',
  active: true,
}

export function HostelsPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)

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
      setFormError(apiErrorMessage(error, 'Could not create hostel'))
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateHostel>[1] }) =>
      updateHostel(id, payload),
    onSuccess: async () => {
      setForm(emptyForm)
      setEditingId(null)
      setFormError(null)
      await queryClient.invalidateQueries({ queryKey: ['hostels'] })
    },
    onError: (error: unknown) => {
      setFormError(apiErrorMessage(error, 'Could not update hostel'))
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: deactivateHostel,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['hostels'] })
    },
  })

  const reactivateMutation = useMutation({
    mutationFn: (id: string) => updateHostel(id, { active: true }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['hostels'] })
    },
  })

  function startEdit(hostel: Hostel) {
    setEditingId(hostel.id)
    setFormError(null)
    setForm({
      name: hostel.name,
      code: hostel.code,
      address: hostel.address ?? '',
      contact_name: hostel.contact_name ?? '',
      phone: hostel.phone ?? '',
      default_rate_per_liter: hostel.default_rate_per_liter,
      active: hostel.active,
    })
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    const payload = {
      name: form.name.trim(),
      code: form.code.trim(),
      address: form.address.trim() || null,
      contact_name: form.contact_name.trim() || null,
      phone: form.phone.trim() || null,
      default_rate_per_liter: form.default_rate_per_liter.trim(),
    }
    if (editingId) {
      updateMutation.mutate({ id: editingId, payload: { ...payload, active: form.active } })
      return
    }
    createMutation.mutate(payload)
  }

  const items = hostelsQuery.data?.items ?? []

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Hostels</h1>
      <p className="mt-2 text-slate-600">Master data for supply locations and default rates.</p>

      <section className="mt-8 mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">
          {editingId ? 'Edit hostel' : 'Add hostel'}
        </h2>
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
          {editingId && (
            <label className="flex items-center gap-2 text-sm text-slate-700 sm:col-span-2">
              <input
                type="checkbox"
                checked={form.active}
                onChange={(event) =>
                  setForm((current) => ({ ...current, active: event.target.checked }))
                }
              />
              Active
            </label>
          )}
          {formError && <p className="sm:col-span-2 text-sm text-red-600">{formError}</p>}
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Saving…'
                : editingId
                  ? 'Save changes'
                  : 'Save hostel'}
            </button>
            {editingId && (
              <button
                type="button"
                className="ml-3 rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                onClick={() => {
                  setEditingId(null)
                  setForm(emptyForm)
                  setFormError(null)
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Hostel list</h2>

        {hostelsQuery.isLoading && <PageLoading message="Loading hostels…" />}
        {hostelsQuery.isError && (
          <PageError message="Could not load hostels. Is the backend running?" />
        )}
        {hostelsQuery.isSuccess && items.length === 0 && (
          <PageEmpty message="No hostels yet. Add one above." />
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
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                    onClick={() => startEdit(hostel)}
                  >
                    Edit
                  </button>
                  {hostel.active ? (
                    <button
                      type="button"
                      className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                      disabled={deactivateMutation.isPending}
                      onClick={() => deactivateMutation.mutate(hostel.id)}
                    >
                      Deactivate
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                      disabled={reactivateMutation.isPending}
                      onClick={() => reactivateMutation.mutate(hostel.id)}
                    >
                      Reactivate
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
