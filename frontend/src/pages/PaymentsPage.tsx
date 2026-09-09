import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiErrorMessage } from '../api/errors'
import { listInvoices } from '../api/invoices'
import { createPayment, listPayments } from '../api/payments'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'
import type { PaymentMethod } from '../types/payment'

const fieldClass = 'rounded-xl border border-slate-200 px-3 py-2'
const methods: PaymentMethod[] = ['cash', 'upi', 'bank_transfer', 'cheque', 'other']

export function PaymentsPage() {
  const queryClient = useQueryClient()
  const [invoiceId, setInvoiceId] = useState('')
  const [amount, setAmount] = useState('')
  const [paymentDate, setPaymentDate] = useState('')
  const [method, setMethod] = useState<PaymentMethod>('upi')
  const [reference, setReference] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [filterInvoice, setFilterInvoice] = useState('')

  const invoicesQuery = useQuery({
    queryKey: ['invoices'],
    queryFn: ({ signal }) => listInvoices({}, signal),
  })

  const paymentsQuery = useQuery({
    queryKey: ['payments', filterInvoice],
    queryFn: ({ signal }) =>
      listPayments({ invoice_id: filterInvoice || undefined }, signal),
  })

  const createMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: async () => {
      setAmount('')
      setReference('')
      setFormError(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['payments'] }),
        queryClient.invalidateQueries({ queryKey: ['invoices'] }),
        queryClient.invalidateQueries({ queryKey: ['invoice'] }),
      ])
    },
    onError: (error: unknown) => {
      setFormError(apiErrorMessage(error, 'Could not save payment'))
    },
  })

  const invoices = invoicesQuery.data?.items ?? []
  const items = paymentsQuery.data?.items ?? []
  const selectedInvoice = invoices.find((invoice) => invoice.id === invoiceId)

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    createMutation.mutate({
      invoice_id: invoiceId,
      amount,
      payment_date: paymentDate,
      payment_method: method,
      reference_number: reference.trim() || null,
    })
  }

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Payments</h1>
      <p className="mt-2 text-slate-600">Record a payment against an invoice. Status updates after save.</p>

      <section className="mt-8 mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Record payment</h2>
        <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={onSubmit}>
          <label className="grid gap-1 text-sm text-slate-700 sm:col-span-2">
            Invoice
            <select
              required
              className={fieldClass}
              value={invoiceId}
              onChange={(event) => setInvoiceId(event.target.value)}
            >
              <option value="">Select invoice</option>
              {invoices.map((invoice) => (
                <option key={invoice.id} value={invoice.id}>
                  {invoice.invoice_number} · ₹{invoice.total_amount} · {invoice.payment_status}
                </option>
              ))}
            </select>
          </label>
          {selectedInvoice && (
            <p className="text-sm text-slate-600 sm:col-span-2">
              Current status: <span className="font-semibold">{selectedInvoice.payment_status}</span>
            </p>
          )}
          <label className="grid gap-1 text-sm text-slate-700">
            Amount (₹)
            <input
              required
              type="number"
              min="0.01"
              step="0.01"
              className={fieldClass}
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Payment date
            <input
              required
              type="date"
              className={fieldClass}
              value={paymentDate}
              onChange={(event) => setPaymentDate(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Method
            <select
              required
              className={fieldClass}
              value={method}
              onChange={(event) => setMethod(event.target.value as PaymentMethod)}
            >
              {methods.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Reference
            <input
              className={fieldClass}
              maxLength={80}
              value={reference}
              onChange={(event) => setReference(event.target.value)}
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
              {createMutation.isPending ? 'Saving…' : 'Save payment'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Payment list</h2>
        <label className="mt-4 grid max-w-md gap-1 text-sm text-slate-700">
          Filter by invoice
          <select
            className={fieldClass}
            value={filterInvoice}
            onChange={(event) => setFilterInvoice(event.target.value)}
          >
            <option value="">All invoices</option>
            {invoices.map((invoice) => (
              <option key={invoice.id} value={invoice.id}>
                {invoice.invoice_number}
              </option>
            ))}
          </select>
        </label>

        {paymentsQuery.isLoading && <PageLoading message="Loading payments…" />}
        {paymentsQuery.isError && (
          <PageError message="Could not load payments. Is the backend running?" />
        )}
        {paymentsQuery.isSuccess && items.length === 0 && (
          <PageEmpty
            message={
              filterInvoice
                ? 'No payments match this invoice.'
                : 'No payments recorded yet.'
            }
          />
        )}

        {items.length > 0 && (
          <ul className="mt-6 divide-y divide-slate-100">
            {items.map((payment) => {
              const invoice = invoices.find((item) => item.id === payment.invoice_id)
              return (
                <li key={payment.id} className="py-4">
                  <p className="font-semibold text-slate-900">
                    ₹{payment.amount} · {payment.payment_method} · {payment.payment_date}
                  </p>
                  <p className="text-sm text-slate-600">
                    {invoice
                      ? `${invoice.invoice_number} · status ${invoice.payment_status}`
                      : payment.invoice_id}
                    {payment.reference_number ? ` · ref ${payment.reference_number}` : ''}
                  </p>
                </li>
              )
            })}
          </ul>
        )}
      </section>
    </div>
  )
}
