import { useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createDelivery, listDeliveries } from '../api/deliveries'
import { apiErrorMessage } from '../api/errors'
import { listHostels } from '../api/hostels'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'
import { hostelLabel } from '../utils/hostels'

const fieldClass = 'rounded-xl border border-slate-200 px-3 py-2'

export function DeliveriesPage() {
  const queryClient = useQueryClient()
  const [hostelId, setHostelId] = useState('')
  const [deliveryDate, setDeliveryDate] = useState('')
  const [morning, setMorning] = useState('')
  const [evening, setEvening] = useState('')
  const [notes, setNotes] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [filterHostel, setFilterHostel] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const hostelsQuery = useQuery({
    queryKey: ['hostels'],
    queryFn: ({ signal }) => listHostels(signal),
  })

  const deliveriesQuery = useQuery({
    queryKey: ['deliveries', filterHostel, dateFrom, dateTo],
    queryFn: ({ signal }) =>
      listDeliveries(
        {
          hostel_id: filterHostel || undefined,
          from: dateFrom || undefined,
          to: dateTo || undefined,
        },
        signal,
      ),
  })

  const createMutation = useMutation({
    mutationFn: createDelivery,
    onSuccess: async () => {
      setMorning('')
      setEvening('')
      setNotes('')
      setFormError(null)
      await queryClient.invalidateQueries({ queryKey: ['deliveries'] })
    },
    onError: (error: unknown) => {
      setFormError(apiErrorMessage(error, 'Could not save delivery'))
    },
  })

  const computedTotal = useMemo(() => {
    const morningValue = Number(morning) || 0
    const eveningValue = Number(evening) || 0
    return (morningValue + eveningValue).toFixed(3)
  }, [morning, evening])

  const hostels = hostelsQuery.data?.items ?? []
  const items = deliveriesQuery.data?.items ?? []
  const hasListFilters = Boolean(filterHostel || dateFrom || dateTo)

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    createMutation.mutate({
      hostel_id: hostelId,
      delivery_date: deliveryDate,
      morning_quantity: morning,
      evening_quantity: evening,
      notes: notes.trim() || null,
    })
  }

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Deliveries</h1>
      <p className="mt-2 text-slate-600">Record morning and evening supply. Total is calculated here for display only.</p>

      <section className="mt-8 mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Add delivery</h2>
        <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={onSubmit}>
          <label className="grid gap-1 text-sm text-slate-700">
            Hostel
            <select
              required
              className={fieldClass}
              value={hostelId}
              onChange={(event) => setHostelId(event.target.value)}
            >
              <option value="">Select hostel</option>
              {hostels
                .filter((hostel) => hostel.active)
                .map((hostel) => (
                  <option key={hostel.id} value={hostel.id}>
                    {hostel.name} ({hostel.code})
                  </option>
                ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Date
            <input
              required
              type="date"
              className={fieldClass}
              value={deliveryDate}
              onChange={(event) => setDeliveryDate(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Morning quantity (L)
            <input
              required
              type="number"
              min="0"
              step="0.001"
              className={fieldClass}
              value={morning}
              onChange={(event) => setMorning(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Evening quantity (L)
            <input
              required
              type="number"
              min="0"
              step="0.001"
              className={fieldClass}
              value={evening}
              onChange={(event) => setEvening(event.target.value)}
            />
          </label>
          <p className="text-sm text-slate-700 sm:col-span-2">
            Computed total:{' '}
            <span className="font-semibold text-slate-900">{computedTotal} L</span>
            <span className="text-slate-500"> (server stores morning + evening)</span>
          </p>
          <label className="grid gap-1 text-sm text-slate-700 sm:col-span-2">
            Notes
            <input
              className={fieldClass}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>
          {formError && (
            <p className="sm:col-span-2 text-sm text-red-600" role="alert">
              {formError}
            </p>
          )}
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {createMutation.isPending ? 'Saving…' : 'Save delivery'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Delivery list</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <label className="grid gap-1 text-sm text-slate-700">
            Hostel
            <select
              className={fieldClass}
              value={filterHostel}
              onChange={(event) => setFilterHostel(event.target.value)}
            >
              <option value="">All hostels</option>
              {hostels.map((hostel) => (
                <option key={hostel.id} value={hostel.id}>
                  {hostel.name} ({hostel.code})
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            From
            <input
              type="date"
              className={fieldClass}
              value={dateFrom}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            To
            <input
              type="date"
              className={fieldClass}
              value={dateTo}
              onChange={(event) => setDateTo(event.target.value)}
            />
          </label>
        </div>

        {deliveriesQuery.isLoading && <PageLoading message="Loading deliveries…" />}
        {deliveriesQuery.isError && (
          <PageError message="Could not load deliveries. Is the backend running?" />
        )}
        {deliveriesQuery.isSuccess && items.length === 0 && (
          <PageEmpty
            message={
              hasListFilters
                ? 'No deliveries match these filters.'
                : 'No deliveries yet. Add one above.'
            }
          />
        )}

        {items.length > 0 && (
          <ul className="mt-6 divide-y divide-slate-100">
            {items.map((delivery) => (
              <li key={delivery.id} className="py-4">
                <p className="font-semibold text-slate-900">
                  {hostelLabel(hostels, delivery.hostel_id)} · {delivery.delivery_date}
                </p>
                <p className="text-sm text-slate-600">
                  Morning {delivery.morning_quantity} L + evening {delivery.evening_quantity} L ={' '}
                  {delivery.total_quantity} L · ₹{delivery.rate_per_liter}/L
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
