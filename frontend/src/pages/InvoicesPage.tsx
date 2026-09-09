import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiErrorMessage } from '../api/errors'
import { listHostels } from '../api/hostels'
import { createInvoice, getInvoice, listInvoices } from '../api/invoices'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'
import { hostelLabel } from '../utils/hostels'

const fieldClass = 'rounded-xl border border-slate-200 px-3 py-2'

export function InvoicesPage() {
  const queryClient = useQueryClient()
  const [hostelId, setHostelId] = useState('')
  const [billingMonth, setBillingMonth] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [filterHostel, setFilterHostel] = useState('')
  const [filterMonth, setFilterMonth] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const hostelsQuery = useQuery({
    queryKey: ['hostels'],
    queryFn: ({ signal }) => listHostels(signal),
  })

  const invoicesQuery = useQuery({
    queryKey: ['invoices', filterHostel, filterMonth, filterStatus],
    queryFn: ({ signal }) =>
      listInvoices(
        {
          hostel_id: filterHostel || undefined,
          billing_month: filterMonth || undefined,
          payment_status: filterStatus || undefined,
        },
        signal,
      ),
  })

  const detailQuery = useQuery({
    queryKey: ['invoice', selectedId],
    queryFn: ({ signal }) => getInvoice(selectedId!, signal),
    enabled: Boolean(selectedId),
  })

  const createMutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: async (invoice) => {
      setFormError(null)
      setSelectedId(invoice.id)
      await queryClient.invalidateQueries({ queryKey: ['invoices'] })
    },
    onError: (error: unknown) => {
      setFormError(apiErrorMessage(error, 'Could not create invoice'))
    },
  })

  const hostels = hostelsQuery.data?.items ?? []
  const items = invoicesQuery.data?.items ?? []
  const hasListFilters = Boolean(filterHostel || filterMonth || filterStatus)

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    createMutation.mutate({ hostel_id: hostelId, billing_month: billingMonth })
  }

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Invoices</h1>
      <p className="mt-2 text-slate-600">Create a monthly invoice from verified delivery totals.</p>

      <section className="mt-8 mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Create invoice</h2>
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
            Billing month
            <input
              required
              type="month"
              className={fieldClass}
              value={billingMonth}
              onChange={(event) => setBillingMonth(event.target.value)}
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
              {createMutation.isPending ? 'Creating…' : 'Create invoice'}
            </button>
          </div>
        </form>
      </section>

      <section className="mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Invoice list</h2>
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
            Month
            <input
              type="month"
              className={fieldClass}
              value={filterMonth}
              onChange={(event) => setFilterMonth(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Payment status
            <select
              className={fieldClass}
              value={filterStatus}
              onChange={(event) => setFilterStatus(event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="unpaid">unpaid</option>
              <option value="partial">partial</option>
              <option value="paid">paid</option>
              <option value="overdue">overdue</option>
            </select>
          </label>
        </div>

        {invoicesQuery.isLoading && <PageLoading message="Loading invoices…" />}
        {invoicesQuery.isError && (
          <PageError message="Could not load invoices. Is the backend running?" />
        )}
        {invoicesQuery.isSuccess && items.length === 0 && (
          <PageEmpty
            message={
              hasListFilters
                ? 'No invoices match these filters.'
                : 'No invoices yet. Create one above.'
            }
          />
        )}

        {items.length > 0 && (
          <ul className="mt-6 divide-y divide-slate-100">
            {items.map((invoice) => (
              <li key={invoice.id} className="flex flex-wrap items-center justify-between gap-3 py-4">
                <div>
                  <p className="font-semibold text-slate-900">{invoice.invoice_number}</p>
                  <p className="text-sm text-slate-600">
                    {hostelLabel(hostels, invoice.hostel_id)} · {invoice.billing_month} · ₹
                    {invoice.total_amount} · {invoice.payment_status}
                  </p>
                </div>
                <button
                  type="button"
                  className="rounded-xl border border-slate-200 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                  onClick={() => setSelectedId(invoice.id)}
                >
                  View
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selectedId && (
        <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
          <h2 className="text-lg font-semibold text-slate-900">Invoice detail</h2>
          {detailQuery.isLoading && <PageLoading message="Loading invoice…" />}
          {detailQuery.isError && <PageError message="Could not load invoice detail." />}
          {detailQuery.data && (
            <div className="mt-4">
              <p className="font-semibold text-slate-900">{detailQuery.data.invoice_number}</p>
              <p className="mt-1 text-sm text-slate-600">
                {hostelLabel(hostels, detailQuery.data.hostel_id)} · {detailQuery.data.billing_month}{' '}
                · status {detailQuery.data.payment_status}
              </p>
              <p className="mt-1 text-sm text-slate-600">
                Period {detailQuery.data.period_start} – {detailQuery.data.period_end} · due{' '}
                {detailQuery.data.due_date}
              </p>
              <p className="mt-2 text-sm text-slate-700">
                Qty {detailQuery.data.total_quantity} L · subtotal ₹{detailQuery.data.subtotal} · tax
                ₹{detailQuery.data.tax} · adj ₹{detailQuery.data.adjustments} · total ₹
                {detailQuery.data.total_amount}
              </p>
              <ul className="mt-4 divide-y divide-slate-100">
                {detailQuery.data.items.map((item) => (
                  <li key={item.id} className="py-3 text-sm text-slate-700">
                    {item.description} · {item.quantity} × ₹{item.rate} = ₹{item.amount}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  )
}
